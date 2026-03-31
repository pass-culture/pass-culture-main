import { screen } from '@testing-library/react'
import type { ComponentProps } from 'react'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1/new'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffersCardVariant, type OffersCardVariant } from '../types'
import { CollectiveOffersCard } from './CollectiveOffersCard'

vi.mock('@/ui-kit/Skeleton/Skeleton', () => ({
  Skeleton: () => <div>skeleton</div>,
}))

vi.mock('../OffersEmptyStateCard/OffersEmptyStateCard', () => ({
  OffersEmptyStateCard: () => <div>empty state</div>,
}))

vi.mock('../OffersRetentionCard/OffersRetentionCard', () => ({
  OffersRetentionCard: ({ variant }: { variant: OffersCardVariant }) => (
    <div>retention {variant}</div>
  ),
}))

const defaultProps = {
  variant: CollectiveOffersCardVariant.TEMPLATE,
  isLoading: false,
  hasOffers: false,
  offersToDisplay: [],
}

const renderCollectiveOffersCard = (
  props?: Partial<ComponentProps<typeof CollectiveOffersCard>>
) => renderWithProviders(<CollectiveOffersCard {...defaultProps} {...props} />)

describe('CollectiveOffersCard', () => {
  it('should display skeleton when data is loading', () => {
    renderCollectiveOffersCard({ isLoading: true })

    expect(screen.getByText('skeleton')).toBeVisible()
  })

  it('should display empty state when venue has no offers yet', () => {
    renderCollectiveOffersCard()

    expect(screen.getByText('empty state')).toBeVisible()
  })

  it('should display retention empty state when venue has no more offers to display on homepage', () => {
    renderCollectiveOffersCard({ hasOffers: true })
    expect(screen.getByText('retention template')).toBeVisible()
  })

  it('should display bookable offers when venue has bookable offers to display on homepage', async () => {
    renderCollectiveOffersCard({
      variant: CollectiveOffersCardVariant.BOOKABLE,
      hasOffers: true,
      offersToDisplay: [
        {
          allowedActions: [],
          collectiveStock: null,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          id: 1,
          imageUrl: null,
          name: 'mon offre',
        },
      ],
    })

    expect(await screen.findByText('offres réservables')).toBeVisible()
  })

  it('should display template offers when venue has active template offers', async () => {
    renderCollectiveOffersCard({
      hasOffers: true,
      offersToDisplay: [
        {
          allowedActions: [],
          dates: null,
          displayedStatus: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
          id: 1,
          imageUrl: null,
          name: 'mon offre vitrine',
        },
      ],
    })

    expect(
      await screen.findByRole('heading', { level: 2, name: 'offres vitrines' })
    ).toBeVisible()
  })
})
