import { screen } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { ExposureEventType } from '@/apiClient/v1'
import {
  getIndividualOfferFactory,
  getOfferExposureFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OfferExposureCards } from './OfferExposureCards'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferExposure: vi.fn(),
  },
}))

const NOW = new Date('2026-06-23T00:00:00Z')
const DAY_IN_MS = 24 * 60 * 60 * 1000

const daysFromNowToIso = (days: number): string =>
  new Date(NOW.getTime() + days * DAY_IN_MS).toISOString()

const renderOfferExposureCards = ({
  bookingsCount = 0,
  dateCreated = daysFromNowToIso(-112),
}: {
  bookingsCount?: number
  dateCreated?: string
} = {}) => {
  const offer = getIndividualOfferFactory({ bookingsCount, dateCreated })

  return renderWithProviders(<OfferExposureCards offer={offer} />)
}

describe('OfferExposureCards', () => {
  it.each([
    { bookingsCount: 0, expectedLabel: '0 réservation' },
    { bookingsCount: 2, expectedLabel: '2 réservations' },
  ])('should display booking count with correct pluralization', async ({
    bookingsCount,
    expectedLabel,
  }) => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory()
    )

    renderOfferExposureCards({ bookingsCount })

    expect(
      await screen.findByRole('heading', {
        name: 'Statistiques de votre offre',
      })
    ).toBeInTheDocument()
    expect(screen.getByText(expectedLabel)).toBeInTheDocument()
  })

  it('should display the six-month subtitle for old offers', async () => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory()
    )

    renderOfferExposureCards({ dateCreated: daysFromNowToIso(-204) })

    expect(
      await screen.findByText('sur les six derniers mois')
    ).toBeInTheDocument()
  })

  it.each([
    { views: 0, expectedLabel: '0 consultation' },
    { views: 2, expectedLabel: '2 consultations' },
  ])('should display consultations count with correct pluralization', async ({
    views,
    expectedLabel,
  }) => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory({ views })
    )

    renderOfferExposureCards()

    expect(await screen.findByText(expectedLabel)).toBeInTheDocument()
  })

  it.each([
    {
      eventType: ExposureEventType.HEADLINE,
      expectedLabel: '+3 depuis la mise à la une',
    },
    {
      eventType: ExposureEventType.HIGHLIGHT,
      expectedLabel: '+3 depuis le début du temps fort',
    },
    {
      eventType: ExposureEventType.PRO_ADVICE,
      expectedLabel: '+3 depuis l’ajout d’une recommandation',
    },
  ])('should display boosted views with the right event label', async ({
    eventType,
    expectedLabel,
  }) => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory({
        events: [
          {
            type: eventType,
            name: null,
            startDate: daysFromNowToIso(-22),
            endDate: daysFromNowToIso(161),
            viewsOnPeriod: 3,
          },
        ],
      })
    )

    renderOfferExposureCards()

    expect(await screen.findByText(expectedLabel)).toBeInTheDocument()
  })

  it('should not display boosted views when enhancement is not ongoing', async () => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValueOnce(
      getOfferExposureFactory({
        events: [
          {
            type: ExposureEventType.HEADLINE,
            name: null,
            startDate: daysFromNowToIso(-53),
            endDate: daysFromNowToIso(-39),
            viewsOnPeriod: 3,
          },
        ],
      })
    )

    renderOfferExposureCards()

    expect(
      await screen.findByRole('heading', {
        name: 'Statistiques de votre offre',
      })
    ).toBeInTheDocument()
    expect(
      screen.queryByText('3 consultations depuis votre mise à la une')
    ).not.toBeInTheDocument()
  })
})
