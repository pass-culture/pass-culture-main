import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

import { CollectiveOffersBookableCard } from '../CollectiveOffersBookableCard/CollectiveOffersBookableCard'
import { OffersEmptyStateCard } from '../OffersEmptyStateCard/OffersEmptyStateCard'
import { OffersRetentionCard } from '../OffersRetentionCard/OffersRetentionCard'
import type {
  CollectiveOffersCardVariant,
  CollectiveOffersVariantMap,
} from '../types'

type CollectiveOffersCardConfigs = {
  [K in CollectiveOffersCardVariant]: {
    emptyStateVariant: K
    renderOffers: (offers: CollectiveOffersVariantMap[K][]) => React.ReactNode
  }
}

const COLLECTIVE_OFFERS_CARD_CONFIG: CollectiveOffersCardConfigs = {
  BOOKABLE: {
    emptyStateVariant: 'BOOKABLE',
    renderOffers: (offers) => <CollectiveOffersBookableCard offers={offers} />,
  },
  TEMPLATE: {
    emptyStateVariant: 'TEMPLATE',
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40065
    renderOffers: (_offers) => <h2>offres vitrines</h2>,
  },
}

export interface CollectiveOffersCardProps<
  T extends CollectiveOffersCardVariant,
> {
  variant: T
  offersToDisplay: CollectiveOffersVariantMap[T][]
  hasOffers: boolean
  isLoading: boolean
}

export const CollectiveOffersCard = <K extends CollectiveOffersCardVariant>({
  variant,
  offersToDisplay,
  hasOffers,
  isLoading,
}: CollectiveOffersCardProps<K>) => {
  const { emptyStateVariant, renderOffers } =
    COLLECTIVE_OFFERS_CARD_CONFIG[variant]

  if (isLoading) {
    return <Skeleton height="15rem" width="100%" />
  }

  if (!hasOffers && offersToDisplay.length === 0) {
    return <OffersEmptyStateCard variant={emptyStateVariant} />
  }

  if (hasOffers && offersToDisplay.length === 0) {
    return <OffersRetentionCard variant={emptyStateVariant} />
  }

  return renderOffers(offersToDisplay)
}
