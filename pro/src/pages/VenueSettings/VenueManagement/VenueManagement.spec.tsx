import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

const { syncVenueMock } = vi.hoisted(() => ({
  syncVenueMock: vi.fn(),
}))

vi.mock('@/commons/hooks/useSyncVenueCache', () => ({
  useSyncVenueCache: () => ({ syncVenue: syncVenueMock }),
}))

const venue = makeGetVenueResponseModel({ id: 1 })
const offerer = {
  ...defaultGetOffererResponseModel,
  managedVenues: [],
}

const renderVenueManagement = () =>
  renderWithProviders(<VenueManagement />, {
    storeOverrides: {
      user: {
        selectedPartnerVenue: venue,
        selectedAdminOfferer: offerer,
      },
    },
  })

import { Component as VenueManagement } from './VenueManagement'

describe('VenueManagement', () => {
  beforeEach(() => {
    vi.spyOn(api, 'closeVenue').mockResolvedValue()
    syncVenueMock.mockResolvedValue(undefined)
  })

  it('should render the banner and the button', () => {
    renderVenueManagement()

    expect(screen.getByText('Fermeture de la structure')).toBeVisible()
    expect(
      screen.getByText('Toutes vos offres seront retirées du pass Culture.')
    ).toBeVisible()
    expect(
      screen.getByRole('button', { name: /Fermer la structure/ })
    ).toBeVisible()
  })

  it('should open the close venue modal', async () => {
    renderVenueManagement()
    const user = userEvent.setup()
    await user.click(
      screen.getByRole('button', { name: /Fermer la structure/ })
    )

    expect(
      screen.getByRole('heading', {
        name: 'Vous souhaitez fermer votre structure ?',
      })
    ).toBeVisible()
  })

  it('should close the venue and synchronize it after validation', async () => {
    renderVenueManagement()
    const user = userEvent.setup()
    await user.click(
      screen.getByRole('button', { name: /Fermer la structure/ })
    )
    await user.click(screen.getByRole('checkbox'))
    await user.click(
      screen.getByRole('button', {
        name: 'Confirmer la demande de fermeture',
      })
    )

    await waitFor(() => {
      expect(api.closeVenue).toHaveBeenCalledWith({
        path: { venue_id: 1 },
      })
    })
    expect(syncVenueMock).toHaveBeenCalledWith(1)
    expect(
      screen.getByRole('heading', {
        name: 'Votre demande de fermeture a bien été prise en compte.',
      })
    ).toBeVisible()
  })

  it('should not open the confirmation modal when closing the venue fails', async () => {
    vi.mocked(api.closeVenue).mockRejectedValue(new Error('Request failed'))
    renderVenueManagement()
    const user = userEvent.setup()
    await user.click(
      screen.getByRole('button', { name: /Fermer la structure/ })
    )
    await user.click(screen.getByRole('checkbox'))
    await user.click(
      screen.getByRole('button', {
        name: 'Confirmer la demande de fermeture',
      })
    )

    await waitFor(() => {
      expect(api.closeVenue).toHaveBeenCalled()
    })
    expect(
      screen.queryByRole('heading', {
        name: 'Votre demande de fermeture a bien été prise en compte.',
      })
    ).not.toBeInTheDocument()
  })
})
