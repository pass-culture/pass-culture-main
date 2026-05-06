import { screen, waitFor } from '@testing-library/react'

import { apiNew } from '@/apiClient/api'
import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import type { CollectiveOffersCardVariant } from '../types'
import { CollectiveOffersCardsContainer } from './CollectiveOffersCardsContainer'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    getCollectiveOffersHome: vi.fn(),
    getCollectiveOfferTemplatesHome: vi.fn(),
  },
}))

vi.mock('../CollectiveOffersCard/CollectiveOffersCard', () => ({
  CollectiveOffersCard: ({
    variant,
  }: {
    variant: CollectiveOffersCardVariant
  }) => <div data-testid={`card-${variant.toLowerCase()}`}>offres</div>,
}))

describe('CollectiveOffersCardsContainer', () => {
  beforeEach(() => {
    vi.spyOn(apiNew, 'getCollectiveOfferTemplatesHome').mockResolvedValue({
      hasOffers: true,
      offers: [],
    })
  })

  it('should render template offers before bookable offers when venue has no bookable offers to display', async () => {
    vi.spyOn(apiNew, 'getCollectiveOffersHome').mockResolvedValueOnce({
      hasOffers: true,
      offers: [],
    })

    renderWithProviders(<CollectiveOffersCardsContainer venueId={1} />)

    // cards rendered with fallback data on first render while waiting for SWR to fetch data
    const cardsFirstRender = screen.getAllByTestId(/^card-/)
    expect(cardsFirstRender[0]).toHaveAttribute('data-testid', 'card-template')
    expect(cardsFirstRender[1]).toHaveAttribute('data-testid', 'card-bookable')

    const cardsSecondRender = cardsFirstRender

    // We need waitFor here instead of findAllBy, because :
    //   - `findAllBy` returns immediately since the elements are already there, so it returns the old ones.
    //   - `waitFor` retries until the method it wraps returns no error. So it retries until the `expect` passes.
    await waitFor(() => {
      const cardsSecondRender = screen.getAllByTestId(/^card-/)
      expect(cardsSecondRender[0]).toHaveAttribute(
        'data-testid',
        'card-template'
      )
    })
    expect(cardsSecondRender[1]).toHaveAttribute('data-testid', 'card-bookable')
  })

  it('should render bookable offers before template offers when venue has only bookable offers to display', async () => {
    vi.spyOn(apiNew, 'getCollectiveOffersHome').mockResolvedValueOnce({
      hasOffers: true,
      offers: [
        {
          allowedActions: [],
          collectiveStock: null,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          id: 1,
          imageUrl: null,
          name: 'mon offre réservable',
        },
      ],
    })
    renderWithProviders(<CollectiveOffersCardsContainer venueId={1} />)

    // cards rendered with fallback data on first render while waiting for SWR to fetch data
    const cardsFirstRender = screen.getAllByTestId(/^card-/)
    expect(cardsFirstRender[0]).toHaveAttribute('data-testid', 'card-template')
    expect(cardsFirstRender[1]).toHaveAttribute('data-testid', 'card-bookable')

    let cardsSecondRender = cardsFirstRender
    await waitFor(() => {
      cardsSecondRender = screen.getAllByTestId(/^card-/)
      expect(cardsSecondRender[0]).toHaveAttribute(
        'data-testid',
        'card-bookable'
      )
    })
    expect(cardsSecondRender[1]).toHaveAttribute('data-testid', 'card-template')
  })
})
