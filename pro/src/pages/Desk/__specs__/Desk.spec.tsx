import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'

import { api, apiContremarque } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { defaultGetBookingResponse } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { Desk } from '../Desk'

const renderDesk = () => {
  renderWithProviders(
    <Routes>
      <Route path="/guichet" element={<Desk />} />
    </Routes>,
    {
      initialRouterEntries: ['/guichet'],
    }
  )
}

describe('Desk', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
  })

  describe('should validate while user is typing', () => {
    it('should remove QRcode prefix', async () => {
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AA:ZERRZ')
      expect(contremarque).toHaveValue('ZERRZ')
    })

    it('should display default messages and disable submit button', async () => {
      renderDesk()
      await waitFor(async () => {
        const message = await screen.findByText('Saisissez une contremarque')
        expect(message).toBeInTheDocument()
      })
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
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockResolvedValue(
        defaultGetBookingResponse
      )
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AAAAAA')
      expect(apiContremarque.getBookingByTokenV2).toHaveBeenCalledWith('AAAAAA')
      expect(
        await screen.findByText(
          'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
        )
      ).toBeInTheDocument()
      expect(
        await screen.findByText(defaultGetBookingResponse.offerName)
      ).toBeInTheDocument()
    })

    it('should display error message when validation fails', async () => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {},
            status: 503,
          } as ApiResult,
          'Oups, an error occured'
        )
      )
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AAAAAA')
      expect(
        await screen.findByText(/Oups, an error occured/)
      ).toBeInTheDocument()
    })
  })

  describe('should validate contremarque when the user submits the form', () => {
    beforeEach(() => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockResolvedValueOnce(
        defaultGetBookingResponse
      )
    })
    it('should display confirmation message and empty field when contremarque is validated', async () => {
      vi.spyOn(
        apiContremarque,
        'patchBookingUseByToken'
      ).mockResolvedValueOnce()
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AAAAAA')
      await userEvent.click(screen.getByText('Valider la contremarque'))
      expect(screen.getByTestId('desk-message')).toContainHTML(
        'Contremarque validée !'
      )
      expect(contremarque).toHaveValue('')
    })

    it('should display error message and empty field when contremarque could not be validated', async () => {
      vi.spyOn(apiContremarque, 'patchBookingUseByToken').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {
              global: 'Erreur',
            },
            status: 503,
          } as ApiResult,
          'api error'
        )
      )
      renderDesk()
      const contremarque = screen.getByLabelText('Contremarque')
      await userEvent.type(contremarque, 'AAAAAA')
      await userEvent.click(screen.getByText('Valider la contremarque'))
      expect(await screen.findByText(/Erreur/)).toBeInTheDocument()
      expect(contremarque).toHaveValue('AAAAAA')
    })
  })

  describe('should invalidate contremarque when the user submits the form', () => {
    beforeEach(() => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {},
            status: 410,
          } as ApiResult,
          'api error'
        )
      )
    })

    it('should display invalidating message when waiting for invalidation and display invalidation confirmation', async () => {
      vi.spyOn(
        apiContremarque,
        'patchBookingKeepByToken'
      ).mockResolvedValueOnce()
      renderDesk()

      await userEvent.type(screen.getByLabelText('Contremarque'), 'AAAAAA')
      await userEvent.click(screen.getByText('Invalider la contremarque'))

      const confirmModalButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmModalButton)

      await waitFor(() => {
        expect(screen.getByTestId('desk-message')).toContainHTML(
          'Contremarque invalidée !'
        )
      })
    })

    it('should display error message when invalidation failed', async () => {
      vi.spyOn(apiContremarque, 'patchBookingKeepByToken').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {},
            status: 500,
          } as ApiResult,
          'Erreur lors de la validation de la contremarque'
        )
      )

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
