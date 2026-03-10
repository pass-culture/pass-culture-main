import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { ApiError } from '@/apiClient/adage'
import type { ApiRequestOptions } from '@/apiClient/adage/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/adage/core/ApiResult'
import { api } from '@/apiClient/api'
import { HTTP_STATUS } from '@/apiClient/helpers'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { defaultGetBookingResponse } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Desk } from './Desk'

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

const snackBarSuccess = vi.fn()
const snackBarError = vi.fn()

describe('Desk', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })

    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      success: snackBarSuccess,
      error: snackBarError,
    }))
  })

  describe('should validate while user is typing', () => {
    it('should remove QRcode prefix', async () => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )

      renderDesk()

      const contremarque = screen.getByLabelText('Contremarque')

      await userEvent.type(contremarque, 'AA:ZERRZ')

      expect(contremarque).toHaveValue('ZERRZ')
    })

    it('should indicate the number of characters missing and indicate the maximum number of caracters', async () => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )

      renderDesk()

      expect(screen.getByText('0/6')).toBeInTheDocument()

      const contremarque = screen.getByLabelText('Contremarque')

      await userEvent.type(contremarque, 'AA')

      expect(screen.getByText('2/6')).toBeInTheDocument()
    })

    it('should indicate the minimum number of caracters', async () => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )

      renderDesk()

      const contremarque = screen.getByLabelText('Contremarque')

      await userEvent.type(contremarque, 'AAOK')

      const validateBtn = screen.getByRole('button', {
        name: 'Valider la contremarque',
      })

      await userEvent.click(validateBtn)

      expect(
        screen.getByText('La contremarque doit contenir 6 caractères')
      ).toBeInTheDocument()
    })

    it('should indicate that the format is invalid and which characters are valid', async () => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )

      renderDesk()

      const contremarque = screen.getByRole('textbox', { name: 'Contremarque' })
      await userEvent.type(contremarque, '@678HJ')

      const validateBtn = screen.getByRole('button', {
        name: 'Valider la contremarque',
      })

      await userEvent.click(validateBtn)

      expect(
        screen.getByText('Caractères valides : de A à Z et de 0 à 9')
      ).toBeInTheDocument()
    })

    it('should check that token is valid and display booking details', async () => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )

      renderDesk()

      const contremarque = screen.getByRole('textbox', { name: 'Contremarque' })
      await userEvent.type(contremarque, 'AAAAAA')

      expect(api.getBookingByToken).toHaveBeenCalledWith('AAAAAA')
      expect(
        await screen.findByText(defaultGetBookingResponse.offerName)
      ).toBeInTheDocument()
    })

    it('should display error message when validation fails', async () => {
      vi.spyOn(api, 'getBookingByToken').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {},
            status: 404,
          } as ApiResult,
          'Not found'
        )
      )

      renderDesk()

      const contremarque = screen.getByRole('textbox', { name: 'Contremarque' })
      await userEvent.type(contremarque, 'AAAAAA')

      waitFor(() => {
        expect(screen.getByText(/Not found/)).toBeInTheDocument()
      })
    })
  })

  describe('should validate contremarque when the user submits the form', () => {
    it('should display confirmation message and empty field when contremarque is validated', async () => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )
      vi.spyOn(api, 'patchBookingUseByToken').mockResolvedValueOnce()

      renderDesk()

      const contremarque = screen.getByRole('textbox', { name: 'Contremarque' })
      await userEvent.type(contremarque, 'AAAAAA')

      const validateBtn = screen.getByRole('button', {
        name: 'Valider la contremarque',
      })

      userEvent.click(validateBtn)

      waitFor(() => {
        expect(snackBarSuccess).toHaveBeenCalledWith('Contremarque validée')
        expect(contremarque).toHaveValue('')
      })
    })

    it('should display error message and empty field when contremarque could not be validated', async () => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )
      vi.spyOn(api, 'patchBookingUseByToken').mockRejectedValue(
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
    it('should display invalidating message when waiting for invalidation and display invalidation confirmation', async () => {
      vi.spyOn(api, 'getBookingByToken').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {},
            status: HTTP_STATUS.GONE,
          } as ApiResult,
          'Already validated'
        )
      )
      vi.spyOn(api, 'patchBookingKeepByToken').mockResolvedValueOnce()

      renderDesk()

      const contremarque = screen.getByRole('textbox', { name: 'Contremarque' })
      await userEvent.type(contremarque, 'AAAAAA')

      const invalidateBtn = screen.getByText('Invalider la contremarque')

      await userEvent.click(invalidateBtn)

      const confirmModalButton = screen.getByRole('button', {
        name: 'Continuer',
      })

      await userEvent.click(confirmModalButton)

      await waitFor(() => {
        expect(snackBarSuccess).toHaveBeenCalledWith('Contremarque invalidée')
      })
    })

    it('should display error message when invalidation failed', async () => {
      vi.spyOn(api, 'getBookingByToken').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {},
            status: 410,
          } as ApiResult,
          'Already validated'
        )
      )
      vi.spyOn(api, 'patchBookingKeepByToken').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {},
            status: 410,
          } as ApiResult,
          'Erreur lors de la validation de la contremarque'
        )
      )

      renderDesk()

      const contremarque = screen.getByRole('textbox', { name: 'Contremarque' })
      await userEvent.type(contremarque, 'AAAAAA')

      const invalidateBtn = screen.getByText('Invalider la contremarque')

      await userEvent.click(invalidateBtn)

      const confirmModalButton = screen.getByRole('button', {
        name: 'Continuer',
      })

      await userEvent.click(confirmModalButton)

      expect(snackBarError).toHaveBeenCalledWith(
        'Erreur lors de la validation de la contremarque'
      )
    })
  })
})
