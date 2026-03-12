import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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

/* -------------------------------------------------------------------------- */
/*                                   Helpers                                  */
/* -------------------------------------------------------------------------- */

const snackBarSuccess = vi.fn()
const snackBarError = vi.fn()

const renderDesk = () =>
  renderWithProviders(
    <Routes>
      <Route path="/guichet" element={<Desk />} />
    </Routes>,
    { initialRouterEntries: ['/guichet'] }
  )

beforeEach(() => {
  vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
    success: snackBarSuccess,
    error: snackBarError,
  }))
})

describe('Desk', () => {
  /* ---------------------------------------------------------------------- */
  /*                              Token typing                              */
  /* ---------------------------------------------------------------------- */

  describe('token typing behaviour', () => {
    it('removes QR code prefix', async () => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )

      const user = userEvent.setup()
      renderDesk()

      const input = screen.getByRole('textbox', { name: 'Contremarque' })
      await user.type(input, 'ZERRZ')

      expect(input).toHaveValue('ZERRZ')
    })

    it('updates character counter', async () => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )

      const user = userEvent.setup()
      renderDesk()

      expect(screen.getByText('0/6')).toBeInTheDocument()

      const input = screen.getByRole('textbox', { name: 'Contremarque' })
      await user.type(input, 'AA')

      expect(screen.getByText('2/6')).toBeInTheDocument()
    })

    it('calls API and displays booking details when token valid', async () => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )

      const user = userEvent.setup()
      renderDesk()

      const input = screen.getByRole('textbox', { name: 'Contremarque' })
      await user.type(input, 'AAAAAA')

      expect(api.getBookingByToken).toHaveBeenCalledWith('AAAAAA')

      expect(
        await screen.findByText(defaultGetBookingResponse.offerName)
      ).toBeInTheDocument()
    })
  })

  /* ---------------------------------------------------------------------- */
  /*                           Form validation (YUP)                        */
  /* ---------------------------------------------------------------------- */

  describe('form validation', () => {
    beforeEach(() => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )
    })

    it('shows error when token shorter than 6 characters', async () => {
      const user = userEvent.setup()
      renderDesk()

      const input = screen.getByRole('textbox', { name: 'Contremarque' })
      await user.type(input, 'AAOK')

      await user.click(
        screen.getByRole('button', {
          name: 'Valider la contremarque',
        })
      )

      expect(
        screen.getByText('La contremarque doit contenir 6 caractères')
      ).toBeInTheDocument()
    })

    it('shows invalid format message', async () => {
      const user = userEvent.setup()
      renderDesk()

      const input = screen.getByRole('textbox', { name: 'Contremarque' })
      await user.type(input, '@678HJ')

      await user.click(
        screen.getByRole('button', {
          name: 'Valider la contremarque',
        })
      )

      expect(
        screen.getByText('Caractères valides : de A à Z et de 0 à 9')
      ).toBeInTheDocument()
    })
  })

  /* ---------------------------------------------------------------------- */
  /*                          Token validation flow                          */
  /* ---------------------------------------------------------------------- */

  describe('validate contremarque', () => {
    beforeEach(() => {
      vi.spyOn(api, 'getBookingByToken').mockResolvedValue(
        defaultGetBookingResponse
      )
    })

    it('validates token successfully', async () => {
      vi.spyOn(api, 'patchBookingUseByToken').mockResolvedValueOnce()

      const user = userEvent.setup()
      renderDesk()

      const input = screen.getByRole('textbox', { name: 'Contremarque' })
      await user.type(input, 'AAAAAA')

      await user.click(
        screen.getByRole('button', {
          name: 'Valider la contremarque',
        })
      )

      expect(snackBarSuccess).toHaveBeenCalledWith('Contremarque validée')

      expect(input).toHaveValue('')
    })

    it('shows API error message when validation fails', async () => {
      vi.spyOn(api, 'patchBookingUseByToken').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: { global: 'Erreur' },
            status: 503,
          } as ApiResult,
          'api error'
        )
      )

      const user = userEvent.setup()
      renderDesk()

      const input = screen.getByRole('textbox', { name: 'Contremarque' })
      await user.type(input, 'AAAAAA')

      await user.click(
        screen.getByRole('button', { name: 'Valider la contremarque' })
      )

      expect(snackBarError).toHaveBeenCalledWith('Erreur')

      expect(input).toHaveValue('AAAAAA')
    })
  })

  /* ---------------------------------------------------------------------- */
  /*                         Token invalidation flow                         */
  /* ---------------------------------------------------------------------- */

  describe('invalidate contremarque', () => {
    beforeEach(() => {
      vi.spyOn(api, 'getBookingByToken').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          { body: {}, status: HTTP_STATUS.GONE } as ApiResult,
          'Already validated'
        )
      )
    })

    it('invalidates token successfully', async () => {
      vi.spyOn(api, 'patchBookingKeepByToken').mockResolvedValueOnce()

      const user = userEvent.setup()
      renderDesk()

      const input = screen.getByRole('textbox', { name: 'Contremarque' })
      await user.type(input, 'AAAAAA')

      await user.click(
        await screen.findByRole('button', { name: 'Invalider la contremarque' })
      )

      await user.click(screen.getByRole('button', { name: 'Continuer' }))

      expect(snackBarSuccess).toHaveBeenCalledWith('Contremarque invalidée')

      expect(input).toHaveValue('')
    })

    it('shows error when invalidation fails', async () => {
      vi.spyOn(api, 'patchBookingKeepByToken').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          { body: {}, status: 410 } as ApiResult,
          'Erreur lors de la validation de la contremarque'
        )
      )

      const user = userEvent.setup()
      renderDesk()

      const input = screen.getByRole('textbox', { name: 'Contremarque' })
      await user.type(input, 'AAAAAA')

      await user.click(
        await screen.findByRole('button', { name: 'Invalider la contremarque' })
      )
      await user.click(screen.getByRole('button', { name: 'Continuer' }))

      expect(
        screen.getByText(/Erreur lors de la validation de la contremarque/)
      ).toBeInTheDocument()
    })
  })
})
