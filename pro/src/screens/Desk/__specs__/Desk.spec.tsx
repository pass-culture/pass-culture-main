import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { clearInputText } from 'utils/testHelpers'

import { DeskScreen, IDeskProps } from '..'

const renderDeskScreen = async (props: IDeskProps) => {
  const rtlReturns = render(
    <MemoryRouter>
      <DeskScreen {...props} />
    </MemoryRouter>
  )

  const pageTitle = await screen.findByRole('heading', { name: 'Guichet' })

  return {
    ...rtlReturns,
    pageTitle,
    inputToken: screen.getByLabelText('Contremarque'),
    messageContainer: screen.getByTestId('desk-message'),
    buttonSubmitValidated: screen.getByText('Valider la contremarque'),
  }
}

describe('src | components | Desk', () => {
  const deskBooking = {
    datetime: '2001-02-01T20:00:00Z',
    ean13: 'test ean113',
    offerName: 'Nom de la structure',
    price: 13,
    quantity: 1,
    userName: 'USER',
    venueDepartmentCode: '75',
  }
  const defaultProps: IDeskProps = {
    getBooking: jest.fn().mockResolvedValue({ booking: deskBooking }),
    submitValidate: jest.fn().mockResolvedValue({}),
    submitInvalidate: jest.fn().mockResolvedValue({}),
  }
  let props: IDeskProps = { ...defaultProps }

  beforeEach(() => {
    props = { ...defaultProps }
  })

  it('test form render', async () => {
    // when
    const { pageTitle, inputToken, buttonSubmitValidated } =
      await renderDeskScreen(props)

    expect(pageTitle).toBeInTheDocument()
    expect(inputToken).toBeInTheDocument()

    const description = screen.getByText(
      'Saisissez les contremarques présentées par les bénéficiaires afin de les valider ou de les invalider.'
    )
    expect(description).toBeInTheDocument()
    expect(props.getBooking).not.toHaveBeenCalled()
    expect(buttonSubmitValidated).toBeInTheDocument()
    expect(buttonSubmitValidated).toBeDisabled()
  })

  it('test token client side validation', async () => {
    const expectedMessage = {
      default: 'Saisissez une contremarque',
      invalidSyntax: 'Caractères valides : de A à Z et de 0 à 9',
      tooShort: 'Caractères restants :',
      tooLong: 'La contremarque ne peut pas faire plus de 6 caractères',
    }

    const { messageContainer, inputToken } = await renderDeskScreen(props)
    expect(messageContainer.textContent).toBe(expectedMessage.default)

    userEvent.paste(inputToken, 'AA"-,')
    expect(messageContainer.textContent).toBe(expectedMessage.invalidSyntax)

    clearInputText(inputToken)
    userEvent.paste(inputToken, 'AA')
    expect(messageContainer.textContent).toContain(expectedMessage.tooShort)

    clearInputText(inputToken)
    userEvent.paste(inputToken, 'AAAAAAA')
    expect(messageContainer.textContent).toBe(expectedMessage.tooLong)

    expect(props.getBooking).not.toHaveBeenCalled()
  })

  it('test valid token and booking details display', async () => {
    const { messageContainer, inputToken, buttonSubmitValidated } =
      await renderDeskScreen(props)

    userEvent.paste(inputToken, 'AAAAAA')
    await waitFor(() => {
      expect(messageContainer.textContent).toBe(
        'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
      )
    })
    expect(props.getBooking).toHaveBeenCalledWith('AAAAAA')
    expect(buttonSubmitValidated).toBeEnabled()

    expect(screen.getByText(deskBooking.userName)).toBeInTheDocument()
    expect(screen.getByText(deskBooking.offerName)).toBeInTheDocument()
    // 2001-02-01T20:00:00Z displayed as 01/02/2001 - 21h00
    expect(screen.getByText('01/02/2001 - 21h00')).toBeInTheDocument()
    expect(screen.getByText(`${deskBooking.price} €`)).toBeInTheDocument()
  })

  it('test token server error', async () => {
    const alreadyValidatedErrorMessage = {
      message: 'server error',
      isTokenValidated: false,
    }
    props = {
      ...props,
      getBooking: jest.fn().mockResolvedValue({
        error: alreadyValidatedErrorMessage,
      }),
    }
    const { messageContainer, inputToken, buttonSubmitValidated } =
      await renderDeskScreen(props)

    userEvent.paste(inputToken, 'AAAAAA')
    await waitFor(() => {
      expect(messageContainer.textContent).toBe(
        alreadyValidatedErrorMessage.message
      )
    })
    expect(props.getBooking).toHaveBeenCalledWith('AAAAAA')
    expect(buttonSubmitValidated).toBeDisabled()
    const buttonSubmitInvalidated = screen.queryByText(
      'Invalider la contremarque'
    )
    expect(buttonSubmitInvalidated).not.toBeInTheDocument()
  })

  it('test validate token submit success', async () => {
    const { messageContainer, inputToken, buttonSubmitValidated } =
      await renderDeskScreen(props)

    userEvent.paste(inputToken, 'AAAAAA')
    await waitFor(() => {
      expect(messageContainer.textContent).toBe(
        'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
      )
    })
    userEvent.click(buttonSubmitValidated)
    expect(messageContainer.textContent).toBe('Validation en cours...')

    await waitFor(() => {
      expect(messageContainer.textContent).toBe('Contremarque validée !')
    })
    expect(props.submitValidate).toHaveBeenCalledWith('AAAAAA')
    expect(inputToken).toHaveValue('')
    expect(buttonSubmitValidated).toBeDisabled()
  })

  it('test already valided token and booking details display', async () => {
    const alreadyValidatedErrorMessage = {
      message: 'Token already validated',
      isTokenValidated: true,
    }
    props = {
      ...props,
      getBooking: jest.fn().mockResolvedValue({
        error: alreadyValidatedErrorMessage,
      }),
    }
    const { messageContainer, inputToken, buttonSubmitValidated } =
      await renderDeskScreen(props)

    userEvent.paste(inputToken, 'AAAAAA')
    await waitFor(() => {
      expect(messageContainer.textContent).toBe(
        alreadyValidatedErrorMessage.message
      )
    })
    expect(props.getBooking).toHaveBeenCalledWith('AAAAAA')

    expect(buttonSubmitValidated).not.toBeInTheDocument()
    const buttonSubmitInvalidated = screen.queryByText(
      'Invalider la contremarque'
    )
    expect(buttonSubmitInvalidated).toBeInTheDocument()
    expect(buttonSubmitInvalidated).toBeEnabled()

    expect(screen.queryByText(deskBooking.userName)).not.toBeInTheDocument()
    expect(screen.queryByText(deskBooking.offerName)).not.toBeInTheDocument()
    // 2001-02-01T20:00:00Z displayed as 01/02/2001 - 21h00
    expect(screen.queryByText('01/02/2001 - 21h00')).not.toBeInTheDocument()
    expect(screen.queryByText(`${deskBooking.price} €`)).not.toBeInTheDocument()
  })

  it('test invalidate token submit success', async () => {
    const alreadyValidatedErrorMessage = {
      message: 'Token already validated',
      isTokenValidated: true,
    }
    props = {
      ...props,
      getBooking: jest.fn().mockResolvedValue({
        error: alreadyValidatedErrorMessage,
      }),
    }
    const { messageContainer, inputToken, buttonSubmitValidated } =
      await renderDeskScreen(props)

    userEvent.paste(inputToken, 'AAAAAA')
    await waitFor(() => {
      expect(messageContainer.textContent).toBe(
        alreadyValidatedErrorMessage.message
      )
    })
    const buttonSubmitInvalidated = await screen.findByText(
      'Invalider la contremarque'
    )
    userEvent.click(buttonSubmitInvalidated)

    const modalConfirmButton = await screen.findByRole('button', {
      name: 'Continuer',
    })
    userEvent.click(modalConfirmButton)

    await waitFor(() => {
      expect(messageContainer.textContent).toBe('Contremarque invalidée !')
    })
    expect(props.submitInvalidate).toHaveBeenCalledWith('AAAAAA')
    expect(inputToken).toHaveValue('')
    expect(buttonSubmitInvalidated).not.toBeInTheDocument()
    expect(buttonSubmitValidated).toBeDisabled()
  })
})
