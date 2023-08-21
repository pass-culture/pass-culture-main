import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { CancelablePromise } from 'apiClient/v1'
import { defaultBookingResponse } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import * as getBookingAdapter from '../adapters/getBooking'
import * as submitTokenAdapter from '../adapters/submitToken'
import Desk from '../Desk'
import { DeskSubmitResponse, MESSAGE_VARIANT } from '../types'

const renderDesk = () => {
  renderWithProviders(<Desk />)
}

describe('src | components | Desk', () => {
  describe('Should validate while user is typing', () => {
    it('should remove QRcode prefix', async () => {
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AA:ZERRZ')
      expect(contremarque).toHaveValue('ZERRZ')
    })

    it('should display default messages and disable submit button', async () => {
      renderDesk()
      expect(screen.getByText('Saisissez une contremarque')).toBeInTheDocument()
      expect(
        screen.getByText(
          'Saisissez les contremarques présentées par les bénéficiaires afin de les valider ou de les invalider.'
        )
      ).toBeInTheDocument()
      expect(screen.getByText('Valider la contremarque')).toBeDisabled()
    })

    it('should indicate the number of characters missing', async () => {
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AA')
      expect(screen.getByText('Caractères restants : 4/6')).toBeInTheDocument()
    })

    it('should indicate the maximum number of caracters', async () => {
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AAOURIRIR')
      expect(
        screen.getByText(
          'La contremarque ne peut pas faire plus de 6 caractères'
        )
      ).toBeInTheDocument()
    })

    it('should indicate that the format is invalid and which characters are valid', async () => {
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AA-@')
      expect(
        screen.getByText('Caractères valides : de A à Z et de 0 à 9')
      ).toBeInTheDocument()
    })

    it('should check that token is valid and display booking details', async () => {
      vi.spyOn(getBookingAdapter, 'getBooking').mockResolvedValue({
        booking: defaultBookingResponse,
      })
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AAAAAA')
      expect(getBookingAdapter.getBooking).toHaveBeenCalledWith('AAAAAA')
      expect(
        await screen.findByText(
          'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
        )
      ).toBeInTheDocument()
      expect(
        await screen.findByText(defaultBookingResponse.offerName)
      ).toBeInTheDocument()
    })

    it('should display error message when validation fails', async () => {
      vi.spyOn(getBookingAdapter, 'getBooking').mockResolvedValue({
        error: {
          message: 'Erreur',
          isTokenValidated: false,
          variant: MESSAGE_VARIANT.ERROR,
        },
      })
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AAAAAA')
      expect(await screen.findByText(/Erreur/)).toBeInTheDocument()
    })
  })

  describe('Should validate contremarque when the user submits the form', () => {
    beforeEach(() => {
      vi.spyOn(getBookingAdapter, 'getBooking').mockResolvedValueOnce({
        booking: defaultBookingResponse,
      })
    })
    it('should display confirmation message and empty field when contremarque is validated', async () => {
      vi.spyOn(submitTokenAdapter, 'submitValidate').mockResolvedValueOnce({})
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AAAAAA')
      await userEvent.click(screen.getByText('Valider la contremarque'))
      expect(
        await screen.findByText('Contremarque validée !')
      ).toBeInTheDocument()
      expect(contremarque).toHaveValue('')
    })

    it('should display error message and empty field when contremarque could not be validated', async () => {
      vi.spyOn(submitTokenAdapter, 'submitValidate').mockResolvedValueOnce({
        error: {
          message: 'Erreur',
          variant: MESSAGE_VARIANT.ERROR,
        },
      })
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AAAAAA')
      await userEvent.click(screen.getByText('Valider la contremarque'))
      expect(await screen.findByText(/Erreur/)).toBeInTheDocument()
      expect(contremarque).toHaveValue('AAAAAA')
    })
  })

  describe('Should invalidate contremarque when the user submits the form', () => {
    beforeEach(() => {
      vi.spyOn(getBookingAdapter, 'getBooking').mockResolvedValueOnce({
        error: {
          isTokenValidated: true,
          message: '',
          variant: MESSAGE_VARIANT.ERROR,
        },
      })
    })

    it('should display invaladating message when waiting for invalidation', async () => {
      vi.spyOn(submitTokenAdapter, 'submitInvalidate').mockImplementation(
        () => {
          return new CancelablePromise<DeskSubmitResponse>(resolve =>
            setTimeout(() => resolve({} as DeskSubmitResponse), 50)
          )
        }
      )
      renderDesk()

      await userEvent.type(screen.getByLabelText('Contremarque'), 'AAAAAA')
      await userEvent.click(screen.getByText('Invalider la contremarque'))

      const confirmModalButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmModalButton)

      expect(screen.getByText('Invalidation en cours...')).toBeInTheDocument()
    })

    it('should display validated message when token invalidation has been done', async () => {
      vi.spyOn(submitTokenAdapter, 'submitInvalidate').mockResolvedValueOnce({})

      renderDesk()

      await userEvent.type(screen.getByLabelText('Contremarque'), 'AAAAAA')
      await userEvent.click(screen.getByText('Invalider la contremarque'))

      const confirmModalButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmModalButton)

      expect(screen.getByText('Contremarque invalidée !')).toBeInTheDocument()
    })

    it('should display error message when invalidation failed', async () => {
      vi.spyOn(submitTokenAdapter, 'submitInvalidate').mockResolvedValueOnce({
        error: {
          message: 'Erreur lors de la validation de la contremarque',
          variant: MESSAGE_VARIANT.ERROR,
        },
      })

      renderDesk()

      await userEvent.type(screen.getByLabelText('Contremarque'), 'AAAAAA')
      await userEvent.click(screen.getByText('Invalider la contremarque'))

      const confirmModalButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmModalButton)
      const errorMessage = await screen.findByText(
        'Erreur lors de la validation de la contremarque'
      )

      expect(errorMessage).toBeInTheDocument()
    })
  })
})
