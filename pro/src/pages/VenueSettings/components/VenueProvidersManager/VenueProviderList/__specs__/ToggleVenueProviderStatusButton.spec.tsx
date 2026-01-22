import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '@/apiClient/api'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultVenueProvider } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ToggleVenueProviderStatusButton } from '../ToggleVenueProviderStatusButton'

const snackBarError = vi.fn()

vi.mock('@/apiClient/api', () => ({
  api: {
    updateVenueProvider: vi.fn(),
  },
}))

const mockMutate = vi.fn()

vi.mock('swr', async () => {
  const actual = await vi.importActual('swr')
  return {
    ...actual,
    useSWRConfig: vi.fn(() => ({
      mutate: mockMutate,
    })),
  }
})

const mockVenue = {
  ...defaultGetVenue,
  id: 1,
}

const mockVenueProvider = {
  ...defaultVenueProvider,
  isActive: true,
}

const renderToggleVenueProviderStatusButton = (
  venueProvider = mockVenueProvider,
  venue = mockVenue
) => {
  renderWithProviders(
    <ToggleVenueProviderStatusButton
      venueProvider={venueProvider}
      venue={venue}
    />
  )
}

describe('ToggleVenueProviderStatusButton', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      success: vi.fn(),
      error: snackBarError,
    }))
  })

  describe('onCancel', () => {
    it('should close the modal when cancel is clicked', async () => {
      renderToggleVenueProviderStatusButton()

      // Open the modal
      const pauseButton = screen.getByText('Mettre en pause')
      await userEvent.click(pauseButton)

      // Verify that the modal is open
      await waitFor(() => {
        expect(
          screen.getByText(
            'Voulez-vous mettre en pause la synchronisation de vos offres ?'
          )
        ).toBeInTheDocument()
      })

      // Click on Cancel
      const cancelButton = screen.getByRole('button', { name: 'Annuler' })
      await userEvent.click(cancelButton)

      // Verify that the modal is closed
      await waitFor(() => {
        expect(
          screen.queryByText(
            'Voulez-vous mettre en pause la synchronisation de vos offres ?'
          )
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('updateVenueProviderStatus - success case', () => {
    it('should call api.updateVenueProvider with inverted isActive status, mutate SWR cache and close modal when active', async () => {
      vi.spyOn(api, 'updateVenueProvider').mockResolvedValue(mockVenueProvider)

      renderToggleVenueProviderStatusButton()

      // Open the modal
      const pauseButton = screen.getByText('Mettre en pause')
      await userEvent.click(pauseButton)

      // Confirm the action
      const confirmButton = screen.getByRole('button', {
        name: 'Mettre en pause la synchronisation',
      })
      await userEvent.click(confirmButton)

      await waitFor(() => {
        expect(api.updateVenueProvider).toHaveBeenCalledTimes(1)
      })

      // Verify that the payload is correct
      expect(api.updateVenueProvider).toHaveBeenCalledWith(1, {
        ...mockVenueProvider,
        providerId: mockVenueProvider.provider.id,
        isActive: false, // Inversé car isActive était true
      })

      // Verify that mutate has been called
      await waitFor(() => {
        expect(mockMutate).toHaveBeenCalledWith([
          GET_VENUE_PROVIDERS_QUERY_KEY,
          mockVenue.id,
        ])
      })

      // Verify that the modal is closed
      await waitFor(() => {
        expect(
          screen.queryByText(
            'Voulez-vous mettre en pause la synchronisation de vos offres ?'
          )
        ).not.toBeInTheDocument()
      })
    })

    it('should call api.updateVenueProvider with inverted isActive status, mutate SWR cache and close modal when inactive', async () => {
      const inactiveVenueProvider = {
        ...mockVenueProvider,
        isActive: false,
      }
      vi.spyOn(api, 'updateVenueProvider').mockResolvedValue(
        inactiveVenueProvider
      )

      renderToggleVenueProviderStatusButton(inactiveVenueProvider)

      // Open the modal
      const reactivateButton = screen.getByText('Réactiver')
      await userEvent.click(reactivateButton)

      // Confirm the action
      const confirmButton = screen.getByRole('button', {
        name: 'Réactiver la synchronisation',
      })
      await userEvent.click(confirmButton)

      await waitFor(() => {
        expect(api.updateVenueProvider).toHaveBeenCalledTimes(1)
      })

      // Verify that the payload is correct (isActive is inverted)
      expect(api.updateVenueProvider).toHaveBeenCalledWith(1, {
        ...inactiveVenueProvider,
        providerId: inactiveVenueProvider.provider.id,
        isActive: true, // Inversé car isActive était false
      })

      // Verify that mutate has been called
      await waitFor(() => {
        expect(mockMutate).toHaveBeenCalledWith([
          GET_VENUE_PROVIDERS_QUERY_KEY,
          mockVenue.id,
        ])
      })

      // Verify that the modal is closed
      await waitFor(() => {
        expect(
          screen.queryByText(
            'Vous êtes sur le point de réactiver la synchronisation de vos offres.'
          )
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('updateVenueProviderStatus - error case', () => {
    it('should show error message, not mutate SWR cache and close modal when api.updateVenueProvider fails', async () => {
      const error = new Error('API Error')
      vi.spyOn(api, 'updateVenueProvider').mockRejectedValue(error)

      renderToggleVenueProviderStatusButton()

      // Open the modal
      const pauseButton = screen.getByText('Mettre en pause')
      await userEvent.click(pauseButton)

      // Confirm the action
      const confirmButton = screen.getByRole('button', {
        name: 'Mettre en pause la synchronisation',
      })
      await userEvent.click(confirmButton)

      await waitFor(() => {
        expect(api.updateVenueProvider).toHaveBeenCalledTimes(1)
      })

      // Verify that the error is displayed
      await waitFor(() => {
        expect(snackBarError).toHaveBeenCalledWith(
          'Une erreur est survenue. Merci de réessayer plus tard'
        )
      })

      // Verify that mutate has not been called in case of error
      expect(mockMutate).not.toHaveBeenCalled()

      // Verify that the modal is closed even in case of error
      await waitFor(() => {
        expect(
          screen.queryByText(
            'Voulez-vous mettre en pause la synchronisation de vos offres ?'
          )
        ).not.toBeInTheDocument()
      })
    })
  })
})
