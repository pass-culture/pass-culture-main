import { screen } from '@testing-library/react'
import useSWR, { type SWRResponse } from 'swr'

import { api } from '@/apiClient/api'
import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1/new'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffersCardVariant } from '../types'
import { CollectiveOffersCard } from './CollectiveOffersCard'

vi.mock('swr', async (originalImport) => ({
  ...(await originalImport()),
  default: vi.fn(),
}))
const useSWRMock = vi.mocked(useSWR)

vi.mock('@/apiClient/api', () => ({
  api: {
    getCollectiveOffersHome: vi.fn(),
    getCollectiveOfferTemplatesHome: vi.fn(),
  },
}))

vi.mock('@/ui-kit/Skeleton/Skeleton', () => ({
  Skeleton: () => <div>skeleton</div>,
}))

vi.mock('../OffersEmptyStateCard/OffersEmptyStateCard', () => ({
  OffersEmptyStateCard: () => <div>empty state</div>,
}))

describe('CollectiveOffersCard', () => {
  it('should display skeleton when data is loading', () => {
    useSWRMock.mockReturnValueOnce({
      isLoading: true,
    } as SWRResponse)

    renderWithProviders(
      <CollectiveOffersCard
        venueId={1}
        variant={CollectiveOffersCardVariant.TEMPLATE}
      />
    )

    expect(screen.getByText('skeleton')).toBeVisible()
  })

  it('should display empty state when venue has no offers yet', () => {
    useSWRMock.mockReturnValueOnce({
      isLoading: false,
      data: {
        hasOffers: false,
        offers: [],
      },
    } as SWRResponse)

    renderWithProviders(
      <CollectiveOffersCard
        venueId={1}
        variant={CollectiveOffersCardVariant.TEMPLATE}
      />
    )

    expect(screen.getByText('empty state')).toBeVisible()
  })

  it('should display retention empty state when venue has no more active offers', () => {
    useSWRMock.mockReturnValueOnce({
      isLoading: false,
      data: {
        hasOffers: true,
        offers: [],
      },
    } as SWRResponse)

    renderWithProviders(
      <CollectiveOffersCard
        venueId={1}
        variant={CollectiveOffersCardVariant.TEMPLATE}
      />
    )

    expect(screen.getByText('empty state retention')).toBeVisible()
  })

  it('should display bookable offers when venue has active bookable offers', async () => {
    const getCollectiveOffersHomeSpy = vi.spyOn(api, 'getCollectiveOffersHome')

    useSWRMock.mockImplementationOnce((_key, fetcher) => {
      if (fetcher) {
        fetcher()
      }

      return {
        isLoading: false,
        data: {
          hasOffers: true,
          offers: [
            {
              allowedActions: [],
              collectiveStock: null,
              displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
              id: 1,
              imageUrl: null,
              name: 'mon offre',
            },
          ],
        },
      } as SWRResponse
    })

    renderWithProviders(
      <CollectiveOffersCard
        venueId={1}
        variant={CollectiveOffersCardVariant.BOOKABLE}
      />
    )

    expect(getCollectiveOffersHomeSpy).toHaveBeenCalledOnce()
    expect(await screen.findByText('offres réservables')).toBeVisible()
  })

  it('should display template offers when venue has active template offers', async () => {
    const getCollectiveOfferTemplatesHomeSpy = vi.spyOn(
      api,
      'getCollectiveOfferTemplatesHome'
    )

    useSWRMock.mockImplementationOnce((_key, fetcher) => {
      if (fetcher) {
        fetcher()
      }

      return {
        isLoading: false,
        data: {
          hasOffers: true,
          offers: [
            {
              allowedActions: [],
              dates: null,
              displayedStatus: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
              id: 1,
              imageUrl: null,
              name: 'mon offre vitrine',
            },
          ],
        },
      } as SWRResponse
    })

    renderWithProviders(
      <CollectiveOffersCard
        venueId={1}
        variant={CollectiveOffersCardVariant.TEMPLATE}
      />
    )

    expect(getCollectiveOfferTemplatesHomeSpy).toHaveBeenCalledOnce()
    expect(await screen.findByText('offres vitrines')).toBeVisible()
  })
})
