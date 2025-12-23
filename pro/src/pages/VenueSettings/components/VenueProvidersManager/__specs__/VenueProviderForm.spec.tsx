import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '@/apiClient/api'
import * as apiHelpers from '@/apiClient/helpers'
import type { ProviderResponse } from '@/apiClient/v1'
import { ApiError } from '@/apiClient/v1'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/v1/core/ApiResult'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultVenueProvider } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { VenueProviderForm } from '../VenueProviderForm'

const snackBarSuccess = vi.fn()
const snackBarError = vi.fn()

vi.mock('@/apiClient/api', () => ({
  api: {
    createVenueProvider: vi.fn(),
  },
}))

vi.mock('@/apiClient/helpers', () => ({
  getHumanReadableApiError: vi.fn((error) => `Error: ${error}`),
}))

const mockProvider: ProviderResponse = {
  id: 1,
  name: 'Test Provider',
  hasOffererProvider: false,
  isActive: true,
  enabledForPro: true,
}

const mockVenue = {
  ...defaultGetVenue,
  id: 1,
  siret: '12345678901234',
}

const renderVenueProviderForm = (
  provider: ProviderResponse = mockProvider,
  selectSoftwareButtonRef?: React.RefObject<HTMLButtonElement>
) => {
  const afterSubmit = vi.fn().mockResolvedValue(undefined)

  renderWithProviders(
    <VenueProviderForm
      provider={provider}
      venue={mockVenue}
      afterSubmit={afterSubmit}
      selectSoftwareButtonRef={selectSoftwareButtonRef}
    />
  )

  return { afterSubmit }
}

describe('VenueProviderForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      success: snackBarSuccess,
      error: snackBarError,
    }))
  })

  describe('createVenueProvider - success case', () => {
    it('should call api.createVenueProvider, show success message, call afterSubmit, return true and focus button', async () => {
      const button = document.createElement('button')
      const focusSpy = vi.spyOn(button, 'focus')
      const selectSoftwareButtonRef = {
        current: button,
      } as React.RefObject<HTMLButtonElement>

      vi.spyOn(api, 'createVenueProvider').mockResolvedValue(
        defaultVenueProvider
      )

      const { afterSubmit } = renderVenueProviderForm(
        mockProvider,
        selectSoftwareButtonRef
      )

      const submitButton = screen.getByRole('button', {
        name: 'Lancer la synchronisation',
      })

      await userEvent.click(submitButton)

      const confirmButton = screen.getByRole('button', { name: 'Continuer' })
      await userEvent.click(confirmButton)

      await waitFor(() => {
        expect(api.createVenueProvider).toHaveBeenCalledTimes(1)
      })

      await waitFor(() => {
        expect(snackBarSuccess).toHaveBeenCalledWith(
          'La synchronisation a bien été initiée.'
        )
      })

      await waitFor(() => {
        expect(afterSubmit).toHaveBeenCalledTimes(1)
      })

      expect(focusSpy).toHaveBeenCalled()
    })

    it('should work without selectSoftwareButtonRef', async () => {
      vi.spyOn(api, 'createVenueProvider').mockResolvedValue(
        defaultVenueProvider
      )

      const { afterSubmit } = renderVenueProviderForm(mockProvider, undefined)

      const submitButton = screen.getByRole('button', {
        name: 'Lancer la synchronisation',
      })

      await userEvent.click(submitButton)

      const confirmButton = screen.getByRole('button', { name: 'Continuer' })
      await userEvent.click(confirmButton)

      await waitFor(() => {
        expect(api.createVenueProvider).toHaveBeenCalledTimes(1)
      })

      await waitFor(() => {
        expect(snackBarSuccess).toHaveBeenCalledWith(
          'La synchronisation a bien été initiée.'
        )
      })

      await waitFor(() => {
        expect(afterSubmit).toHaveBeenCalledTimes(1)
      })
    })
  })

  describe('createVenueProvider - error case', () => {
    it('should call api.createVenueProvider, show error message, call afterSubmit, return false and focus button', async () => {
      const button = document.createElement('button')
      const focusSpy = vi.spyOn(button, 'focus')
      const selectSoftwareButtonRef = {
        current: button,
      } as React.RefObject<HTMLButtonElement>

      const error = new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: { global: ['Test error'] },
        } as ApiResult,
        'Test error'
      )

      vi.spyOn(api, 'createVenueProvider').mockRejectedValue(error)
      vi.spyOn(apiHelpers, 'getHumanReadableApiError').mockReturnValue(
        'Test error message'
      )

      const { afterSubmit } = renderVenueProviderForm(
        mockProvider,
        selectSoftwareButtonRef
      )

      const submitButton = screen.getByRole('button', {
        name: 'Lancer la synchronisation',
      })

      await userEvent.click(submitButton)

      const confirmButton = screen.getByRole('button', { name: 'Continuer' })
      await userEvent.click(confirmButton)

      await waitFor(() => {
        expect(api.createVenueProvider).toHaveBeenCalledTimes(1)
      })

      await waitFor(() => {
        expect(apiHelpers.getHumanReadableApiError).toHaveBeenCalledWith(error)
      })

      await waitFor(() => {
        expect(snackBarError).toHaveBeenCalledWith('Test error message')
      })

      await waitFor(() => {
        expect(afterSubmit).toHaveBeenCalledTimes(1)
      })

      expect(focusSpy).toHaveBeenCalled()
    })

    it('should work without selectSoftwareButtonRef on error', async () => {
      const error = new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: { global: ['Test error'] },
        } as ApiResult,
        'Test error'
      )

      vi.spyOn(api, 'createVenueProvider').mockRejectedValue(error)
      vi.spyOn(apiHelpers, 'getHumanReadableApiError').mockReturnValue(
        'Test error message'
      )

      const { afterSubmit } = renderVenueProviderForm(mockProvider, undefined)

      const submitButton = screen.getByRole('button', {
        name: 'Lancer la synchronisation',
      })

      await userEvent.click(submitButton)

      const confirmButton = screen.getByRole('button', { name: 'Continuer' })
      await userEvent.click(confirmButton)

      await waitFor(() => {
        expect(api.createVenueProvider).toHaveBeenCalledTimes(1)
      })

      await waitFor(() => {
        expect(apiHelpers.getHumanReadableApiError).toHaveBeenCalledWith(error)
      })

      await waitFor(() => {
        expect(snackBarError).toHaveBeenCalledWith('Test error message')
      })

      await waitFor(() => {
        expect(afterSubmit).toHaveBeenCalledTimes(1)
      })
    })
  })
})
