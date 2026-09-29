import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { HomepageEvents } from 'commons/core/FirebaseEvents/constants'
import { FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import { defaultOfferHomeResponseModel } from 'commons/utils/factories/individualApiFactories'
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
    listOffersHome: vi.fn(),
    getVenueHeadlineOffer: vi.fn(),
  },
}))

vi.mock('../HighlightHome/ModalHighlight/ModalHighlight', () => ({
  ModalHighlight: ({ isOpen }: { isOpen: boolean }) =>
    isOpen ? <div role="dialog">Panneau temps forts</div> : null,
}))

const logEventMock = vi.fn()
vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => ({ logEvent: logEventMock }),
}))

const renderStatsCard = (
  hasOffers = true,
  features: string[] = [],
  shouldRetryOnError = false
) =>
  renderWithProviders(
    <SWRConfig
      value={{
        // Ensure a fresh, isolated cache per test run
        provider: () => new Map(),
        dedupingInterval: 0,
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
        shouldRetryOnError,
        errorRetryInterval: 1,
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

    it('should show only the headline action when the venue has thing offers', async () => {
      vi.spyOn(api, 'listOffersHome').mockResolvedValue([
        {
          ...defaultOfferHomeResponseModel,
          id: 1,
          isEvent: false,
        },
      ])
      renderStatsCard(true, ['WIP_HOME_STATS_V2'])
      await screen.findByRole('heading', { name: 'Améliorez votre visibilité' })

      const headlineLink = screen.getByRole('link', {
        name: 'Choisir une offre',
      })
      expect(headlineLink).toBeVisible()
      expect(headlineLink).toHaveAttribute('href', '/offres')
      expect(
        screen.queryByRole('button', { name: 'Voir les prochains temps forts' })
      ).toBeNull()
      expect(screen.getByTestId('visibility-actions')).not.toHaveClass(
        'has-both-actions'
      )
    })

    it('should not retry when the venue has no headline offer', async () => {
      vi.spyOn(api, 'getVenueOffersStatsV2').mockResolvedValueOnce(stats)
      vi.spyOn(api, 'listOffersHome').mockResolvedValue([
        {
          ...defaultOfferHomeResponseModel,
          id: 1,
          isEvent: false,
        },
      ])
      vi.spyOn(api, 'getVenueHeadlineOffer').mockRejectedValue({ status: 404 })

      renderStatsCard(true, ['WIP_HOME_STATS_V2'], true)

      await waitFor(() => {
        expect(api.getVenueHeadlineOffer).toHaveBeenCalledTimes(1)
      })
      expect(
        await screen.findByRole('link', { name: 'Choisir une offre' })
      ).toBeVisible()

      expect(api.getVenueHeadlineOffer).toHaveBeenCalledTimes(1)
    })

    it('should show only the highlight action when the venue has event offers', async () => {
      vi.spyOn(api, 'listOffersHome').mockResolvedValue([
        {
          ...defaultOfferHomeResponseModel,
          id: 1,
          isEvent: true,
        },
      ])
      renderStatsCard(true, ['WIP_HOME_STATS_V2'])
      await screen.findByRole('heading', { name: 'Améliorez votre visibilité' })

      expect(
        screen.getByRole('button', { name: 'Voir les prochains temps forts' })
      ).toBeVisible()
      expect(
        screen.queryByRole('link', {
          name: 'Choisir une offre',
        })
      ).toBeNull()
      expect(screen.getByTestId('visibility-actions')).not.toHaveClass(
        'has-both-actions'
      )
    })

    it('should show both actions and open the highlight panel', async () => {
      const user = userEvent.setup()
      vi.spyOn(api, 'listOffersHome').mockResolvedValue([
        {
          ...defaultOfferHomeResponseModel,
          id: 1,
          isEvent: true,
        },
        {
          ...defaultOfferHomeResponseModel,
          id: 2,
          isEvent: false,
        },
      ])
      renderStatsCard(true, ['WIP_HOME_STATS_V2'])
      await screen.findByRole('heading', { name: 'Améliorez votre visibilité' })

      expect(screen.getByTestId('visibility-actions')).toHaveClass(
        'has-both-actions'
      )
      expect(
        screen.getByRole('link', {
          name: 'Choisir une offre',
        })
      ).toBeVisible()

      await user.click(
        screen.getByRole('button', { name: 'Voir les prochains temps forts' })
      )

      expect(screen.getByRole('dialog')).toHaveTextContent(
        'Panneau temps forts'
      )

      await userEvent.click(
        screen.getByRole('link', {
          name: 'Choisir une offre',
        })
      )

      expect(logEventMock).toHaveBeenCalledWith(
        HomepageEvents.CLICKED_HEADLINE_OFFER
      )
    })
  })
})
