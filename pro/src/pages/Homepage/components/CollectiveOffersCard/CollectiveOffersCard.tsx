import type {
  CollectiveOfferHomeResponseModel,
  CollectiveOfferTemplateHomeResponseModel,
} from '@/apiClient/v1/new'
import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

import { OffersEmptyStateCard } from '../OffersEmptyStateCard/OffersEmptyStateCard'
import {
  CollectiveOffersCardVariant,
  OffersEmptyStateCardVariant,
} from '../types'

type OffersHomeResponseModel =
  | CollectiveOfferHomeResponseModel[]
  | CollectiveOfferTemplateHomeResponseModel[]

type CollectiveOffersCardConfig = {
  emptyStateVariant: OffersEmptyStateCardVariant
  renderOffers: (offers: OffersHomeResponseModel) => React.ReactNode
}

const COLLECTIVE_OFFERS_CARD_CONFIG: Record<
  CollectiveOffersCardVariant,
  CollectiveOffersCardConfig
> = {
  [CollectiveOffersCardVariant.BOOKABLE]: {
    emptyStateVariant: OffersEmptyStateCardVariant.BOOKABLE,
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40063
    renderOffers: (_offers) => <div>offres réservables</div>,
  },
  [CollectiveOffersCardVariant.TEMPLATE]: {
    emptyStateVariant: OffersEmptyStateCardVariant.TEMPLATE,
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40065
    renderOffers: (_offers) => <div>offres vitrines</div>,
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
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40066
    return <div>empty state retention</div>
  }

  return renderOffers(offersToDisplay)
}
