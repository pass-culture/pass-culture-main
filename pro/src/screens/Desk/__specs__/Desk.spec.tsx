import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { CancelablePromise } from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DeskScreen, DeskProps, DeskSubmitResponse } from '..'

const renderDeskScreen = (props: DeskProps) => {
  const rtlReturns = renderWithProviders(<DeskScreen {...props} />)

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
    priceCategoryLabel: 'mon label',
    venueDepartmentCode: '75',
  }
  const defaultProps: DeskProps = {
    getBooking: vi.fn(() => Promise.resolve({ booking: deskBooking })),
    submitValidate: vi.fn().mockResolvedValue({}),
    submitInvalidate: vi.fn().mockResolvedValue({}),
  }

  it('test form render', async () => {
    // when
    const { pageTitle, inputToken, buttonSubmitValidated } =
      renderDeskScreen(defaultProps)

    expect(pageTitle).toBeInTheDocument()
    expect(inputToken).toBeInTheDocument()

    const description = screen.getByText(
      'Saisissez les contremarques présentées par les bénéficiaires afin de les valider ou de les invalider.'
    )
    expect(description).toBeInTheDocument()
    expect(defaultProps.getBooking).not.toHaveBeenCalled()
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
    const getBooking = vi.fn()
    const { messageContainer, inputToken } = renderDeskScreen({
      ...defaultProps,
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
    const { inputToken, buttonSubmitValidated } = renderDeskScreen(defaultProps)

    await userEvent.type(inputToken, 'AAAAAA')

    expect(await screen.findByTestId('desk-message')).toHaveTextContent(
      'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
    )

    expect(defaultProps.getBooking).toHaveBeenCalledWith('AAAAAA')
    expect(buttonSubmitValidated).toBeEnabled()

    expect(screen.getByText(deskBooking.userName)).toBeInTheDocument()
    expect(screen.getByText(deskBooking.offerName)).toBeInTheDocument()
    // 2001-02-01T20:00:00Z displayed as 01/02/2001 - 21h00
    expect(screen.getByText('01/02/2001 - 21h00')).toBeInTheDocument()
    expect(screen.getByText(`${deskBooking.price} €`)).toBeInTheDocument()
  })

  it('test token server error', async () => {
    const alreadyValidatedErrorMessage = {
      message: 'server erro',
      isTokenValidated: false,
    }
    const getBookingMock = vi.fn().mockResolvedValue({
      error: alreadyValidatedErrorMessage,
    })

    const { inputToken, buttonSubmitValidated } = renderDeskScreen({
      ...defaultProps,
      getBooking: getBookingMock,
    })

    await userEvent.type(inputToken, 'AAAAAA')

    expect(await screen.findByTestId('desk-message')).toHaveTextContent(
      alreadyValidatedErrorMessage.message
    )

    expect(getBookingMock).toHaveBeenCalledWith('AAAAAA')
    expect(buttonSubmitValidated).toBeDisabled()
    const buttonSubmitInvalidated = screen.queryByText(
      'Invalider la contremarque'
    )
    expect(buttonSubmitInvalidated).not.toBeInTheDocument()
  })

  it('test validate token submit success', async () => {
    const submitValidate = vi.fn().mockImplementation(() => Promise.resolve({}))
    const { inputToken, buttonSubmitValidated } = renderDeskScreen({
      ...defaultProps,
      submitValidate,
    })

    await userEvent.type(inputToken, 'AAAAAA')

    expect(await screen.findByTestId('desk-message')).toHaveTextContent(
      'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
    )

    await userEvent.click(screen.getByText('Valider la contremarque'))

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
    const getBookingMock = vi.fn().mockResolvedValue({
      error: alreadyValidatedErrorMessage,
    })
    const { messageContainer, inputToken, buttonSubmitValidated } =
      renderDeskScreen({
        ...defaultProps,
        getBooking: getBookingMock,
      })

    await userEvent.type(inputToken, 'AAAAAA')
    expect(messageContainer.textContent).toBe(
      alreadyValidatedErrorMessage.message
    )
    expect(getBookingMock).toHaveBeenCalledWith('AAAAAA')

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

  describe('invalidate button clicked', () => {
    it('should display invaladating message when waiting for invalidation', async () => {
      const submitInvalidateMock = vi.fn().mockImplementation(() => {
        return new CancelablePromise<DeskSubmitResponse>(resolve =>
          setTimeout(() => resolve({} as DeskSubmitResponse), 50)
        )
      })

      renderDeskScreen({
        ...defaultProps,
        getBooking: vi.fn().mockResolvedValue({
          error: {
            isTokenValidated: true,
          },
        }),
        submitInvalidate: submitInvalidateMock,
      })

      await userEvent.type(screen.getByLabelText('Contremarque'), 'AAAAAA')
      await userEvent.click(screen.getByText('Invalider la contremarque'))

      const confirmModalButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmModalButton)

      expect(screen.getByText('Invalidation en cours...')).toBeInTheDocument()
    })

    it('should display validated message when token invalidation has been done', async () => {
      const submitInvalidateMock = vi
        .fn()
        .mockImplementation(() => Promise.resolve({}))

      renderDeskScreen({
        ...defaultProps,
        getBooking: vi.fn().mockResolvedValue({
          error: {
            isTokenValidated: true,
          },
        }),
        submitInvalidate: submitInvalidateMock,
      })

      await userEvent.type(screen.getByLabelText('Contremarque'), 'AAAAAA')
      await userEvent.click(screen.getByText('Invalider la contremarque'))

      const confirmModalButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmModalButton)

      expect(screen.getByText('Contremarque invalidée !')).toBeInTheDocument()
    })

    it('should display error message when invalidation failed', async () => {
      const submitInvalidateMock = vi.fn().mockImplementation(() =>
        Promise.resolve({
          error: {
            message: 'Erreur lors de la validation de la contremarque',
            variant: 'error',
          },
        })
      )

      renderDeskScreen({
        ...defaultProps,
        getBooking: vi.fn().mockResolvedValue({
          error: {
            isTokenValidated: true,
          },
        }),
        submitInvalidate: submitInvalidateMock,
      })

      await userEvent.type(screen.getByLabelText('Contremarque'), 'AAAAAA')
      await userEvent.click(screen.getByText('Invalider la contremarque'))

      const confirmModalButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmModalButton)

      expect(
        screen.getByText('Erreur lors de la validation de la contremarque')
      ).toBeInTheDocument()
    })
  })
})
