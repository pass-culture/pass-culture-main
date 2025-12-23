import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { createRef } from 'react'
import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { DeleteVenueProviderButton } from './DeleteVenueProviderButton'

vi.mock('@/apiClient/api', () => ({
  api: {
    deleteVenueProvider: vi.fn(),
  },
}))

const mockMutate = vi.fn()
vi.mock('swr', async () => ({
  ...(await vi.importActual('swr')),
  useSWRConfig: vi.fn(() => ({
    mutate: mockMutate,
  })),
}))

const snackBarError = vi.fn()

const mockVenue = makeGetVenueResponseModel({
  id: 1,
  name: 'Test Venue',
})

const mockSelectSoftwareButtonRef = createRef<HTMLButtonElement>()

const renderDeleteVenueProviderButton = () => {
  return renderWithProviders(
    <>
      <button ref={mockSelectSoftwareButtonRef}>Select Software</button>
      <DeleteVenueProviderButton
        venueProviderId={123}
        venue={mockVenue}
        selectSoftwareButtonRef={mockSelectSoftwareButtonRef}
      />
    </>
  )
}

describe('DeleteVenueProviderButton', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      success: vi.fn(),
      error: snackBarError,
    }))
  })

  it('should open dialog when clicking on delete button', async () => {
    const user = userEvent.setup()
    renderDeleteVenueProviderButton()

    const deleteButton = screen.getByRole('button', { name: 'Supprimer' })
    await user.click(deleteButton)

    expect(
      screen.getByText(
        'Voulez-vous supprimer la synchronisation de vos offres ?'
      )
    ).toBeInTheDocument()
  })

  it('should successfully delete venue provider and close dialog', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'deleteVenueProvider').mockResolvedValueOnce(undefined)
    mockMutate.mockResolvedValueOnce(undefined)

    renderDeleteVenueProviderButton()

    // Create spy on the actual button after it's rendered
    const selectSoftwareButton = screen.getByRole('button', {
      name: 'Select Software',
    })
    const focusSpy = vi.spyOn(selectSoftwareButton, 'focus')

    // Open dialog
    const deleteButton = screen.getByRole('button', { name: 'Supprimer' })
    await user.click(deleteButton)

    // Confirm deletion
    const confirmButton = screen.getByRole('button', {
      name: 'Supprimer la synchronisation',
    })
    await user.click(confirmButton)

    await waitFor(() => {
      expect(api.deleteVenueProvider).toHaveBeenCalledWith(123)
    })

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith([
        GET_VENUE_PROVIDERS_QUERY_KEY,
        mockVenue.id,
      ])
    })

    // Dialog should be closed
    await waitFor(() => {
      expect(
        screen.queryByText(
          'Voulez-vous supprimer la synchronisation de vos offres ?'
        )
      ).not.toBeInTheDocument()
    })

    // Focus should be set on selectSoftwareButtonRef
    await waitFor(() => {
      expect(focusSpy).toHaveBeenCalled()
    })
  })

  it('should display error message when deletion fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'deleteVenueProvider').mockRejectedValueOnce(
      new Error('API Error')
    )

    renderDeleteVenueProviderButton()

    // Create spy on the actual button after it's rendered
    const selectSoftwareButton = screen.getByRole('button', {
      name: 'Select Software',
    })
    const focusSpy = vi.spyOn(selectSoftwareButton, 'focus')

    // Open dialog
    const deleteButton = screen.getByRole('button', { name: 'Supprimer' })
    await user.click(deleteButton)

    // Confirm deletion
    const confirmButton = screen.getByRole('button', {
      name: 'Supprimer la synchronisation',
    })
    await user.click(confirmButton)

    await waitFor(() => {
      expect(api.deleteVenueProvider).toHaveBeenCalledWith(123)
    })

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(
        'Une erreur est survenue. Merci de réessayer plus tard.'
      )
    })

    // Dialog should be closed even on error
    await waitFor(() => {
      expect(
        screen.queryByText(
          'Voulez-vous supprimer la synchronisation de vos offres ?'
        )
      ).not.toBeInTheDocument()
    })

    // Focus should still be set on selectSoftwareButtonRef
    await waitFor(() => {
      expect(focusSpy).toHaveBeenCalled()
    })

    // mutate should not be called on error
    expect(mockMutate).not.toHaveBeenCalled()
  })

  it('should close dialog when clicking cancel', async () => {
    const user = userEvent.setup()
    renderDeleteVenueProviderButton()

    // Open dialog
    const deleteButton = screen.getByRole('button', { name: 'Supprimer' })
    await user.click(deleteButton)

    expect(
      screen.getByText(
        'Voulez-vous supprimer la synchronisation de vos offres ?'
      )
    ).toBeInTheDocument()

    // Cancel deletion
    const cancelButton = screen.getByRole('button', { name: 'Annuler' })
    await user.click(cancelButton)

    // Dialog should be closed
    await waitFor(() => {
      expect(
        screen.queryByText(
          'Voulez-vous supprimer la synchronisation de vos offres ?'
        )
      ).not.toBeInTheDocument()
    })

    // API should not be called
    expect(api.deleteVenueProvider).not.toHaveBeenCalled()
  })
})
