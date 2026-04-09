import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { StatsCard } from './StatsCard'

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenueOffersStats: vi.fn(),
  },
}))

const renderStatsCard = (hasOffers = true) =>
  renderWithProviders(
    <StatsCard
      venue={{
        ...defaultGetVenue,
        hasNonDraftOffers: hasOffers,
      }}
    />,
    {
      user: sharedCurrentUserFactory(),
    }
  )

describe('StatsCard', () => {
  it('should not render the card when there is less than 2 days of data', async () => {
    vi.spyOn(api, 'getVenueOffersStats').mockResolvedValue({
      jsonData: { dailyViews: [], topOffers: [], totalViewsLast30Days: 0 },
      venueId: 1,
    })

    const { container } = renderStatsCard()

    await waitFor(() => {
      expect(api.getVenueOffersStats).toHaveBeenCalled()
    })

    expect(container.innerHTML).toBe('')
  })

  it('should not render the card when there is only 1 day of data', async () => {
    vi.spyOn(api, 'getVenueOffersStats').mockResolvedValue({
      jsonData: {
        dailyViews: [{ day: '2020-10-10', views: 10 }],
        topOffers: [],
        totalViewsLast30Days: 10,
      },
      venueId: 1,
    })

    const { container } = renderStatsCard()

    await waitFor(() => {
      expect(api.getVenueOffersStats).toHaveBeenCalled()
    })

    expect(container.innerHTML).toBe('')
  })

  it('should render the card with stats when there are at least 2 days of data', async () => {
    vi.spyOn(api, 'getVenueOffersStats').mockResolvedValue({
      jsonData: {
        dailyViews: [
          { day: '2020-10-10', views: 10 },
          { day: '2020-10-11', views: 20 },
        ],
        topOffers: [],
        totalViewsLast30Days: 30,
      },
      venueId: 1,
    })

    renderStatsCard()

    expect(
      await screen.findByRole('heading', {
        name: /Les statistiques sur l'individuel/,
      })
    ).toBeVisible()
  })
})
