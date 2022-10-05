import '@testing-library/jest-dom'

import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { DeskScreen, IDeskProps } from '..'

const renderDeskScreen = (props: IDeskProps) => {
  const rtlReturns = render(
    <MemoryRouter>
      <DeskScreen {...props} />
    </MemoryRouter>
  )

  const pageTitle = screen.getByRole('heading', { name: 'Guichet' })

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
      renderDeskScreen(props)

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
    const getBooking = jest.fn()
    const { messageContainer, inputToken } = renderDeskScreen({
      ...props,
      getBooking,
    })
    expect(messageContainer.textContent).toBe(expectedMessage.default)

    await userEvent.type(inputToken, 'AA"-,')
    expect(await screen.findByTestId('desk-message')).toHaveTextContent(
      expectedMessage.invalidSyntax
    )

    await userEvent.clear(inputToken)
    await userEvent.type(inputToken, 'AA')
    expect(messageContainer.textContent).toContain(expectedMessage.tooShort)

    await userEvent.clear(inputToken)
    await userEvent.paste('AAAAAAA')
    expect(messageContainer.textContent).toBe(expectedMessage.tooLong)

    expect(getBooking).not.toHaveBeenCalled()
  })

  it('test valid token and booking details display', async () => {
    const { inputToken, buttonSubmitValidated } = renderDeskScreen(props)

    await userEvent.type(inputToken, 'AAAAAA')

    expect(await screen.findByTestId('desk-message')).toHaveTextContent(
      'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
    )

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
    const { inputToken, buttonSubmitValidated } = renderDeskScreen(props)

    await userEvent.type(inputToken, 'AAAAAA')

    expect(await screen.findByTestId('desk-message')).toHaveTextContent(
      alreadyValidatedErrorMessage.message
    )

    expect(props.getBooking).toHaveBeenCalledWith('AAAAAA')
    expect(buttonSubmitValidated).toBeDisabled()
    const buttonSubmitInvalidated = screen.queryByText(
      'Invalider la contremarque'
    )
    expect(buttonSubmitInvalidated).not.toBeInTheDocument()
  })

  it('test validate token submit success', async () => {
    const submitValidate = jest
      .fn()
      .mockImplementation(() => Promise.resolve({}))
    const { inputToken, buttonSubmitValidated } = renderDeskScreen({
      ...props,
      submitValidate,
    })

    await userEvent.type(inputToken, 'AAAAAA')

    expect(await screen.findByTestId('desk-message')).toHaveTextContent(
      'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
    )

    // I don't know how to test this without fireEvent
    fireEvent.click(screen.getByText('Valider la contremarque'))
    expect(screen.getByText('Validation en cours...')).toBeInTheDocument()

    expect(
      await screen.findByText('Contremarque validée !')
    ).toBeInTheDocument()
    expect(submitValidate).toHaveBeenCalledWith('AAAAAA')
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
      renderDeskScreen(props)

    await userEvent.type(inputToken, 'AAAAAA')
    expect(messageContainer.textContent).toBe(
      alreadyValidatedErrorMessage.message
    )
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
      submitInvalidate: jest.fn().mockImplementation(() => Promise.resolve({})),
    }
    const { inputToken, buttonSubmitValidated } = renderDeskScreen(props)
    await userEvent.clear(inputToken)
    await userEvent.type(inputToken, 'AAAAAA')
    expect(screen.getByTestId('desk-message')).toHaveTextContent(
      alreadyValidatedErrorMessage.message
    )
    const buttonSubmitInvalidated = await screen.findByText(
      'Invalider la contremarque'
    )
    await userEvent.click(buttonSubmitInvalidated)

    const modalConfirmButton = await screen.findByRole('button', {
      name: 'Continuer',
    })

    await userEvent.click(modalConfirmButton)

    expect(
      await screen.findByText('Contremarque invalidée !')
    ).toBeInTheDocument()

    expect(props.submitInvalidate).toHaveBeenCalledWith('AAAAAA')
    expect(inputToken).toHaveValue('')
    expect(buttonSubmitInvalidated).not.toBeInTheDocument()
    expect(buttonSubmitValidated).toBeDisabled()
  })
})
