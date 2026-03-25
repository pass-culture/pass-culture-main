import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type {
  CollectiveOfferTemplatesHomeResponseModel,
  ListCollectiveOffersHomeResponseModel,
} from '@/apiClient/v1/new'
import {
  GET_COLLECTIVE_OFFER_TEMPLATES_HOME_QUERY_KEY,
  GET_COLLECTIVE_OFFERS_HOME_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

import { OffersEmptyStateCard } from '../OffersEmptyStateCard/OffersEmptyStateCard'
import {
  CollectiveOffersCardVariant,
  OffersEmptyStateCardVariant,
} from '../types'

type OffersHomeResponseModel =
  | ListCollectiveOffersHomeResponseModel
  | CollectiveOfferTemplatesHomeResponseModel

type CollectiveOffersCardConfig = {
  queryKey: string
  fetcher: (venueId: number) => Promise<OffersHomeResponseModel>
  emptyStateVariant: OffersEmptyStateCardVariant
  renderOffers: (offers: OffersHomeResponseModel['offers']) => React.ReactNode
}

const COLLECTIVE_OFFERS_CARD_CONFIG: Record<
  CollectiveOffersCardVariant,
  CollectiveOffersCardConfig
> = {
  [CollectiveOffersCardVariant.BOOKABLE]: {
    queryKey: GET_COLLECTIVE_OFFERS_HOME_QUERY_KEY,
    fetcher: (venueId: number) => api.getCollectiveOffersHome(venueId),
    emptyStateVariant: OffersEmptyStateCardVariant.BOOKABLE,
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40063
    renderOffers: (_offers) => <div>offres réservables</div>,
  },
  [CollectiveOffersCardVariant.TEMPLATE]: {
    queryKey: GET_COLLECTIVE_OFFER_TEMPLATES_HOME_QUERY_KEY,
    fetcher: (venueId: number) => api.getCollectiveOfferTemplatesHome(venueId),
    emptyStateVariant: OffersEmptyStateCardVariant.TEMPLATE,
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40065
    renderOffers: (_offers) => <div>offres vitrines</div>,
  },
}

interface CollectiveOffersCardProps {
  venueId: number
  variant: CollectiveOffersCardVariant
}

export const CollectiveOffersCard = ({
  venueId,
  variant,
}: CollectiveOffersCardProps) => {
  const { queryKey, fetcher, emptyStateVariant, renderOffers } =
    COLLECTIVE_OFFERS_CARD_CONFIG[variant]

  const offersQuery = useSWR([queryKey, venueId], () => fetcher(venueId), {
    fallbackData: { hasOffers: false, offers: [] },
  })

  const hasOffers = offersQuery.data?.hasOffers
  const offers = offersQuery.data?.offers

  if (offersQuery.isLoading) {
    return <Skeleton height="15rem" width="100%" />
  }

  if (!hasOffers && offers.length === 0) {
    return <OffersEmptyStateCard variant={emptyStateVariant} />
  }

  if (hasOffers && offers.length === 0) {
    // TODO (ahello - 26/03/25) implement component in https://passculture.atlassian.net/browse/PC-40066
    return <div>empty state retention</div>
  }

  return renderOffers(offers)
}
