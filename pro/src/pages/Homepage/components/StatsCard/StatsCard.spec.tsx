import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import {
  getVenueOffersStatsV2ResponseModelFactory,
  venueMonthlyViewModelFactory,
  venueOffersPeriodStatsModelFactory,
} from 'commons/utils/factories/statisticsFactories'
import { format, subMonths } from 'date-fns'
import { SWRConfig } from 'swr'
import { describe } from 'vitest'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { StatsCard } from './StatsCard'

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenueOffersStats: vi.fn(),
    getVenueOffersStatsV2: vi.fn(),
  },
}))

const renderStatsCard = (hasOffers = true, features: string[] = []) =>
  renderWithProviders(
    <SWRConfig
      value={{
        // Ensure a fresh, isolated cache per test run
        provider: () => new Map(),
        dedupingInterval: 0,
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
        shouldRetryOnError: false,
      }}
    >
      <StatsCard
        venue={{
          ...defaultGetVenue,
          hasNonDraftOffers: hasOffers,
        }}
      />
    </SWRConfig>,
    {
      user: sharedCurrentUserFactory(),
      features,
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

  describe('With WIP_HOME_STATS_V2 FF', () => {
    const stats = getVenueOffersStatsV2ResponseModelFactory()

    it('should render the card', async () => {
      vi.spyOn(api, 'getVenueOffersStatsV2').mockResolvedValueOnce(stats)
      const { container } = renderStatsCard(true, ['WIP_HOME_STATS_V2'])

      await waitFor(() => {
        expect(api.getVenueOffersStatsV2).toHaveBeenCalled()
      })
      expect(await screen.findByText(/0 consultations/)).toBeVisible()

      expect(await axe(container)).toHaveNoViolations()
    })

    it('should render empty state', async () => {
      vi.spyOn(api, 'getVenueOffersStatsV2').mockResolvedValueOnce(stats)
      renderStatsCard(true, ['WIP_HOME_STATS_V2'])

      await waitFor(() => {
        expect(api.getVenueOffersStatsV2).toHaveBeenCalled()
      })
      expect(await screen.findByText(/0 consultations/)).toBeVisible()
      expect(screen.getByText(/sur les 3 derniers mois/)).toBeVisible()
    })

    it('should render six months selected if no data in last 3 months', async () => {
      vi.spyOn(api, 'getVenueOffersStatsV2').mockResolvedValueOnce({
        ...stats,
        last6Months: venueOffersPeriodStatsModelFactory({
          cumulatedViews: 10,
          viewsByMonth: [
            venueMonthlyViewModelFactory({
              views: 10,
              month: format(subMonths(new Date(), 5), FORMAT_ISO_DATE_ONLY),
            }),
          ],
        }),
      })
      renderStatsCard(true, ['WIP_HOME_STATS_V2'])

      await waitFor(() => {
        expect(api.getVenueOffersStatsV2).toHaveBeenCalled()
      })
      expect(await screen.findByText(/10 consultations/)).toBeVisible()
      expect(screen.getByText('sur les 6 derniers mois')).toBeVisible()

      await userEvent.selectOptions(screen.getByRole('combobox'), 'last3Months')
      expect(await screen.findByText(/0 consultations/)).toBeVisible()
      expect(await screen.findByText('sur les 3 derniers mois')).toBeVisible()
    })
  })
})
