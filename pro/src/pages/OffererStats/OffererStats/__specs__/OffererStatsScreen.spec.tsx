import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { CancelablePromise, GetOffererResponseModel } from 'apiClient/v1'
import { defaultGetOffererResponseModel } from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { OffererStatsScreen } from '../OffererStatsScreen'

vi.mock('apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    getOffererStatsDashboardUrl: vi.fn(),
    getVenueStatsDashboardUrl: vi.fn(),
  },
}))

const renderOffererStatsScreen = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<OffererStatsScreen />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: { selectedOffererId: 1, offererNames: [] },
    },
    ...options,
  })
}

describe('OffererStatsScreen', () => {
  let offerers: GetOffererResponseModel[]
  const venueId = 1

  beforeEach(() => {
    offerers = [
      {
        id: 1,
        hasDigitalVenueAtLeastOneOffer: true,
        managedVenues: [
          {
            name: 'Offre numérique',
            isVirtual: true,
            id: venueId,
          },
          { name: 'Salle 1', id: 2 },
          { name: 'Stand popcorn', id: 3 },
        ],
      },
      {
        id: 2,
        managedVenues: [
          { name: 'Terre de livres', id: 4 },
          { name: 'La voie aux chapitres', id: 5 },
        ],
      },
    ] as GetOffererResponseModel[]

    vi.spyOn(api, 'getOfferer').mockImplementation((offererId) => {
      return new CancelablePromise((resolve) =>
        resolve(offerers.filter((offerer) => offerer.id === offererId)[0])
      )
    })
    vi.spyOn(api, 'getOffererStatsDashboardUrl').mockResolvedValue({
      dashboardUrl: 'offererIframeUrl',
    })
    vi.spyOn(api, 'getVenueStatsDashboardUrl').mockResolvedValue({
      dashboardUrl: 'venueIframeUrl',
    })
  })

  it('should get first offerer venues on render', async () => {
    renderOffererStatsScreen()

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })
    const virtualVenueOption = await screen.findByText('Offre numérique')
    const venueOption = screen.getByText('Salle 1')
    expect(virtualVenueOption).toBeInTheDocument()
    expect(venueOption).toBeInTheDocument()
  })

  it('should not display virtual venue if offerer has no digital offer', async () => {
    offerers[0].hasDigitalVenueAtLeastOneOffer = false
    renderOffererStatsScreen()

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })
    const venueOption = await screen.findByText('Salle 1')
    const virtualVenueOption = screen.queryByText('Offre numérique')
    expect(virtualVenueOption).not.toBeInTheDocument()
    expect(venueOption).toBeInTheDocument()
  })

  it('should display not display venue select if offerer has no venue', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    renderOffererStatsScreen()
    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })

    const venueSelect = screen.queryByLabelText('Lieu')
    expect(venueSelect).not.toBeInTheDocument()
  })

  it('should display venue iframe when selecting a venue', async () => {
    renderOffererStatsScreen()
    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })

    const venueSelect = await screen.findByLabelText('Lieu')
    await userEvent.selectOptions(venueSelect, venueId.toString())
    const iframe = screen.getByTitle('Tableau des statistiques')
    expect(iframe).toBeInTheDocument()
    expect(iframe).toHaveAttribute('src', 'venueIframeUrl')
  })

  it('should display offerer stats when selecting all venues', async () => {
    renderOffererStatsScreen()
    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })

    const venueSelect = await screen.findByLabelText('Lieu')
    await userEvent.selectOptions(venueSelect, 'all')
  })

  it('should have good wording for venues with WIP_ENABLE_OFFER_ADDRESS', async () => {
    renderOffererStatsScreen({
      features: ['WIP_ENABLE_OFFER_ADDRESS'],
    })

    expect(
      await screen.findByLabelText('Partenaire culturel')
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('option', { name: 'Tous les lieux' })
    ).not.toBeInTheDocument()

    expect(screen.queryByRole('option', { name: 'Tous' })).toBeInTheDocument()
  })
})
