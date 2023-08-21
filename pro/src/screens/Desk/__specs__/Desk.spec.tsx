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

  it('should remove QRcode prefix', async () => {
    renderDeskScreen(defaultProps)
    const contremarque = screen.getByLabelText('Contremarque')
    await userEvent.type(contremarque, 'AA:ZERRZ')
    expect(contremarque).toHaveValue('ZERRZ')
  })

  it('should display default messages and disable submit button', async () => {
    renderDeskScreen(defaultProps)
    expect(screen.getByText('Saisissez une contremarque')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Saisissez les contremarques présentées par les bénéficiaires afin de les valider ou de les invalider.'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Valider la contremarque')).toBeDisabled()
  })

  it('should indicate the number of characters missing', async () => {
    renderDeskScreen(defaultProps)
    const contremarque = screen.getByLabelText('Contremarque')
    await userEvent.type(contremarque, 'AA')
    expect(screen.getByText('Caractères restants : 4/6')).toBeInTheDocument()
  })

  it('should indicate the maximum number of caracters', async () => {
    renderDeskScreen(defaultProps)
    const contremarque = screen.getByLabelText('Contremarque')
    await userEvent.type(contremarque, 'AAOURIRIR')
    expect(
      screen.getByText('La contremarque ne peut pas faire plus de 6 caractères')
    ).toBeInTheDocument()
  })

  it('should indicate that the format is invalid and which characters are valid', async () => {
    renderDeskScreen(defaultProps)
    const contremarque = screen.getByLabelText('Contremarque')
    await userEvent.type(contremarque, 'AA-@')
    expect(
      screen.getByText('Caractères valides : de A à Z et de 0 à 9')
    ).toBeInTheDocument()
  })

  it('should check that token is valid and display booking details', async () => {
    renderDeskScreen(defaultProps)
    const contremarque = screen.getByLabelText('Contremarque')
    await userEvent.type(contremarque, 'AAAAAA')
    expect(defaultProps.getBooking).toHaveBeenCalledWith('AAAAAA')
    expect(
      await screen.findByText(
        'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
      )
    ).toBeInTheDocument()
    expect(await screen.findByText(deskBooking.offerName)).toBeInTheDocument()
  })

  it('should display error message when validation fails', async () => {
    const getBookingMock = vi.fn().mockResolvedValue({
      error: {
        message: 'Erreur',
        isTokenValidated: true,
      },
    })
    renderDeskScreen({ ...defaultProps, getBooking: getBookingMock })
    const contremarque = screen.getByLabelText('Contremarque')
    await userEvent.type(contremarque, 'AAAAAA')
    expect(await screen.findByText(/Erreur/)).toBeInTheDocument()
  })

  it('should display confirmation message and empty field when contremarque is validated', async () => {
    renderDeskScreen({
      ...defaultProps,
      submitValidate: vi.fn().mockImplementation(() => Promise.resolve({})),
    })
    const contremarque = screen.getByLabelText('Contremarque')
    await userEvent.type(contremarque, 'AAAAAA')
    await userEvent.click(screen.getByText('Valider la contremarque'))
    expect(
      await screen.findByText('Contremarque validée !')
    ).toBeInTheDocument()
    expect(contremarque).toHaveValue('')
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
