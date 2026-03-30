import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

import { CollectiveOffersBookableCard } from '../CollectiveOffersBookableCard/CollectiveOffersBookableCard'
import { OffersEmptyStateCard } from '../OffersEmptyStateCard/OffersEmptyStateCard'
import { OffersRetentionCard } from '../OffersRetentionCard/OffersRetentionCard'
import {
  CollectiveOffersCardVariant,
  type CollectiveOffersVariantMap,
  OffersCardVariant,
} from '../types'

type CollectiveOffersCardConfig<T> = {
  emptyStateVariant: OffersCardVariant
  renderOffers: (offers: T) => React.ReactNode
}

type CollectiveOffersCardConfigs = {
  [K in CollectiveOffersCardVariant]: CollectiveOffersCardConfig<
    CollectiveOffersVariantMap[K][]
  >
}

const COLLECTIVE_OFFERS_CARD_CONFIG: CollectiveOffersCardConfigs = {
  [CollectiveOffersCardVariant.BOOKABLE]: {
    emptyStateVariant: OffersCardVariant.BOOKABLE,
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40063
    renderOffers: (offers) => <CollectiveOffersBookableCard offers={offers} />,
  },
  [CollectiveOffersCardVariant.TEMPLATE]: {
    emptyStateVariant: OffersCardVariant.TEMPLATE,
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40065
    renderOffers: (_offers) => <h2>offres vitrines</h2>,
  },
}

interface CollectiveOffersCardProps<T extends CollectiveOffersCardVariant> {
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
