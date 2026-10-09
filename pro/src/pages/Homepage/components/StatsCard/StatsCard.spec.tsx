import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import { defaultOfferHomeResponseModel } from 'commons/utils/factories/individualApiFactories'
import {
  getVenueOffersStatsV2ResponseModelFactory,
  venueMonthlyViewModelFactory,
  venueOffersPeriodStatsModelFactory,
} from 'commons/utils/factories/statisticsFactories'
import { format, subMonths } from 'date-fns'
import { SWRConfig, useSWRConfig } from 'swr'
import { describe } from 'vitest'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { GET_VENUE_HEADLINE_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
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
  shouldRetryOnError = false,
  hasHighlightRequest = false
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
          hasHighlightRequest,
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

    beforeEach(() => {
      vi.mocked(api.listOffersHome).mockResolvedValue([])
    })

    it('should show visibility advice with a headline offer and no highlight request even without event offers', async () => {
      vi.spyOn(api, 'getVenueOffersStatsV2').mockResolvedValueOnce(stats)
      vi.spyOn(api, 'listOffersHome').mockResolvedValue([])
      vi.spyOn(api, 'getVenueHeadlineOffer').mockResolvedValue({
        id: 1,
        name: 'Offre à la une',
        venueId: defaultGetVenue.id,
      })

      renderStatsCard(true, ['WIP_HOME_STATS_V2'])

      expect(
        await screen.findByRole('heading', {
          name: 'Améliorez votre visibilité',
        })
      ).toBeVisible()
      expect(
        screen.getByRole('link', {
          name: /Voir nos conseils des gestion et valorisation d’offres/,
        })
      ).toBeVisible()
    })

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

    it.each([
      { isEvent: false, hasHeadlineOffer: false, hasHighlightRequest: false },
      { isEvent: false, hasHeadlineOffer: false, hasHighlightRequest: true },
      { isEvent: false, hasHeadlineOffer: true, hasHighlightRequest: false },
      { isEvent: false, hasHeadlineOffer: true, hasHighlightRequest: true },
      { isEvent: true, hasHeadlineOffer: false, hasHighlightRequest: false },
      { isEvent: true, hasHeadlineOffer: false, hasHighlightRequest: true },
      { isEvent: true, hasHeadlineOffer: true, hasHighlightRequest: false },
      { isEvent: true, hasHeadlineOffer: true, hasHighlightRequest: true },
    ])(
      'should display the appropriate actions for event=$isEvent, headline=$hasHeadlineOffer, highlight request=$hasHighlightRequest',
      async ({ isEvent, hasHeadlineOffer, hasHighlightRequest }) => {
        vi.spyOn(api, 'getVenueOffersStatsV2').mockResolvedValueOnce(stats)
        vi.mocked(api.listOffersHome).mockResolvedValue([
          { ...defaultOfferHomeResponseModel, isEvent },
        ])
        if (hasHeadlineOffer) {
          vi.spyOn(api, 'getVenueHeadlineOffer').mockResolvedValue({
            id: 1,
            name: 'Offre à la une',
            venueId: defaultGetVenue.id,
          })
        } else {
          vi.spyOn(api, 'getVenueHeadlineOffer').mockRejectedValue({
            status: 404,
          })
        }

        renderStatsCard(true, ['WIP_HOME_STATS_V2'], false, hasHighlightRequest)

        await screen.findByRole('heading', {
          name: 'Améliorez votre visibilité',
        })
        expect(
          !!screen.queryByRole('link', { name: 'Choisir une offre' })
        ).toBe(!hasHeadlineOffer)
        expect(
          !!screen.queryByRole('button', {
            name: 'Voir les prochains temps forts',
          })
        ).toBe(isEvent && !hasHighlightRequest)
        expect(
          !!screen.queryByRole('link', { name: /Voir nos conseils/ })
        ).toBe(hasHeadlineOffer && (hasHighlightRequest || !isEvent))
        expect(
          screen
            .getByTestId('visibility-actions')
            .classList.contains('has-both-actions')
        ).toBe(!hasHeadlineOffer && isEvent && !hasHighlightRequest)

        if (isEvent && !hasHighlightRequest) {
          await userEvent.click(
            screen.getByRole('button', {
              name: 'Voir les prochains temps forts',
            })
          )
          expect(screen.getByRole('dialog')).toHaveTextContent(
            'Panneau temps forts'
          )
        }
      }
    )

    it('should not retry when the venue has no headline offer', async () => {
      vi.spyOn(api, 'getVenueOffersStatsV2').mockResolvedValueOnce(stats)
      vi.spyOn(api, 'getVenueHeadlineOffer').mockRejectedValue({ status: 404 })

      renderStatsCard(true, ['WIP_HOME_STATS_V2'], true)

      await waitFor(() => {
        expect(api.getVenueHeadlineOffer).toHaveBeenCalledTimes(1)
      })
      await screen.findByText(/0 consultations/)
      expect(
        screen.queryByRole('heading', { name: 'Améliorez votre visibilité' })
      ).not.toBeInTheDocument()

      expect(api.getVenueHeadlineOffer).toHaveBeenCalledTimes(1)
    })

    it.each(['cache removal', '404 revalidation'])(
      'should replace visibility advice with the headline action after headline offer %s',
      async (removalMode) => {
        vi.spyOn(api, 'getVenueOffersStatsV2').mockResolvedValue(stats)
        vi.mocked(api.listOffersHome).mockResolvedValue([
          { ...defaultOfferHomeResponseModel, isEvent: false },
        ])
        vi.spyOn(api, 'getVenueHeadlineOffer')
          .mockResolvedValueOnce({
            id: 1,
            name: 'Offre à la une',
            venueId: defaultGetVenue.id,
          })
          .mockRejectedValue({ status: 404 })

        const RemoveHeadlineOffer = () => {
          const { mutate } = useSWRConfig()
          const headlineKey = [
            GET_VENUE_HEADLINE_OFFER_QUERY_KEY,
            defaultGetVenue.id,
          ]

          return (
            <button
              type="button"
              onClick={() => {
                if (removalMode === 'cache removal') {
                  void mutate(headlineKey, null, { revalidate: false })
                } else {
                  void mutate(headlineKey)
                }
              }}
            >
              Retirer l'offre à la une
            </button>
          )
        }

        renderWithProviders(
          <SWRConfig
            value={{
              provider: () => new Map(),
              dedupingInterval: 0,
              shouldRetryOnError: false,
            }}
          >
            <StatsCard
              venue={{ ...defaultGetVenue, hasHighlightRequest: false }}
            />
            <RemoveHeadlineOffer />
          </SWRConfig>,
          {
            user: sharedCurrentUserFactory(),
            features: ['WIP_HOME_STATS_V2'],
          }
        )

        expect(
          await screen.findByRole('link', { name: /Voir nos conseils/ })
        ).toBeVisible()

        await userEvent.click(
          screen.getByRole('button', { name: "Retirer l'offre à la une" })
        )

        await waitFor(() => {
          expect(
            screen.queryByRole('link', { name: /Voir nos conseils/ })
          ).not.toBeInTheDocument()
        })
        expect(
          screen.getByRole('link', { name: 'Choisir une offre' })
        ).toBeVisible()
      }
    )
  })
})
