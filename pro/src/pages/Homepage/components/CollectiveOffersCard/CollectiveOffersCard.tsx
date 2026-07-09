import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

import { CollectiveOffersBookableCard } from '../CollectiveOffersBookableCard/CollectiveOffersBookableCard'
import { CollectiveOffersTemplateCard } from '../CollectiveOffersTemplateCard/CollectiveOffersTemplateCard'
import { OffersEmptyStateCard } from '../OffersEmptyStateCard/OffersEmptyStateCard'
import { OffersRetentionCard } from '../OffersRetentionCard/OffersRetentionCard'
import {
  type CollectiveOffersCardVariant,
  type CollectiveOffersVariantMap,
  OffersCardVariant,
} from '../types'

type RenderOffersOptions = {
  isReadOnly: boolean
}

type CollectiveOffersCardConfigs = {
  [K in CollectiveOffersCardVariant]: {
    emptyStateVariant: OffersCardVariant
    renderOffers: (
      offers: CollectiveOffersVariantMap[K][],
      options: RenderOffersOptions
    ) => React.ReactNode
  }
}

const COLLECTIVE_OFFERS_CARD_CONFIG: CollectiveOffersCardConfigs = {
  BOOKABLE: {
    emptyStateVariant: OffersCardVariant.BOOKABLE,
    renderOffers: (offers, { isReadOnly }: RenderOffersOptions) => (
      <CollectiveOffersBookableCard isReadOnly={isReadOnly} offers={offers} />
    ),
  },
  TEMPLATE: {
    emptyStateVariant: OffersCardVariant.TEMPLATE,
    renderOffers: (offers, { isReadOnly }: RenderOffersOptions) => (
      <CollectiveOffersTemplateCard isReadOnly={isReadOnly} offers={offers} />
    ),
  },
}

export interface CollectiveOffersCardProps<
  T extends CollectiveOffersCardVariant,
> {
  variant: T
  offersToDisplay: CollectiveOffersVariantMap[T][]
  hasOffers: boolean
  isLoading: boolean
  isReadOnly: boolean
}

export const CollectiveOffersCard = <K extends CollectiveOffersCardVariant>({
  variant,
  offersToDisplay,
  hasOffers,
  isLoading,
  isReadOnly,
}: CollectiveOffersCardProps<K>) => {
  const { emptyStateVariant, renderOffers } =
    COLLECTIVE_OFFERS_CARD_CONFIG[variant]

  if (isLoading) {
    return <Skeleton height="15rem" width="100%" />
  }

  if (!hasOffers && offersToDisplay.length === 0) {
    return (
      <OffersEmptyStateCard
        isReadOnly={isReadOnly}
        variant={emptyStateVariant}
      />
    )
  }

  if (hasOffers && offersToDisplay.length === 0) {
    return (
      <OffersRetentionCard
        isReadOnly={isReadOnly}
        variant={emptyStateVariant}
      />
    )
  }

  return renderOffers(offersToDisplay, { isReadOnly })
}
