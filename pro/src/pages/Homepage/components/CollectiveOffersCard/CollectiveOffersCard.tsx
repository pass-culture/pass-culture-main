import type {
  CollectiveOfferHomeResponseModel,
  CollectiveOfferTemplateHomeResponseModel,
} from '@/apiClient/v1/new'
import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

import { OffersEmptyStateCard } from '../OffersEmptyStateCard/OffersEmptyStateCard'
import { OffersRetentionCard } from '../OffersRetentionCard/OffersRetentionCard'
import { CollectiveOffersCardVariant, OffersCardVariant } from '../types'

type OffersHomeResponseModel =
  | CollectiveOfferHomeResponseModel[]
  | CollectiveOfferTemplateHomeResponseModel[]

type CollectiveOffersCardConfig = {
  emptyStateVariant: OffersCardVariant
  renderOffers: (offers: OffersHomeResponseModel) => React.ReactNode
}

const COLLECTIVE_OFFERS_CARD_CONFIG: Record<
  CollectiveOffersCardVariant,
  CollectiveOffersCardConfig
> = {
  [CollectiveOffersCardVariant.BOOKABLE]: {
    emptyStateVariant: OffersCardVariant.BOOKABLE,
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40063
    renderOffers: (_offers) => <h2>offres réservables</h2>,
  },
  [CollectiveOffersCardVariant.TEMPLATE]: {
    emptyStateVariant: OffersCardVariant.TEMPLATE,
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40065
    renderOffers: (_offers) => <h2>offres vitrines</h2>,
  },
}

interface CollectiveOffersCardProps {
  variant: CollectiveOffersCardVariant
  offersToDisplay:
    | CollectiveOfferHomeResponseModel[]
    | CollectiveOfferTemplateHomeResponseModel[]
  hasOffers: boolean
  isLoading: boolean
}

export const CollectiveOffersCard = ({
  variant,
  offersToDisplay,
  hasOffers,
  isLoading,
}: CollectiveOffersCardProps) => {
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
