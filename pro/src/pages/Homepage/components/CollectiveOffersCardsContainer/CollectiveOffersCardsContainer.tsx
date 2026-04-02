import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  GET_COLLECTIVE_OFFER_TEMPLATES_HOME_QUERY_KEY,
  GET_COLLECTIVE_OFFERS_HOME_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'

import { CollectiveOffersCard } from '../CollectiveOffersCard/CollectiveOffersCard'

export const CollectiveOffersCardsContainer = ({
  venueId,
}: {
  venueId: number
}) => {
  const bookableOffersQuery = useSWR(
    [GET_COLLECTIVE_OFFERS_HOME_QUERY_KEY, venueId],
    () => api.getCollectiveOffersHome(venueId),
    {
      fallbackData: { hasOffers: false, offers: [] },
    }
  )

  const hasBookableOffers = bookableOffersQuery.data?.hasOffers
  const bookableOffers = bookableOffersQuery.data?.offers

  const templateOffersQuery = useSWR(
    [GET_COLLECTIVE_OFFER_TEMPLATES_HOME_QUERY_KEY, venueId],
    () => api.getCollectiveOfferTemplatesHome(venueId),
    {
      fallbackData: { hasOffers: false, offers: [] },
    }
  )

  const hasTemplateOffers = templateOffersQuery.data?.hasOffers
  const templateOffers = templateOffersQuery.data?.offers

  const templateOffersComponent = (
    <CollectiveOffersCard
      variant={'TEMPLATE'}
      offersToDisplay={templateOffers}
      hasOffers={hasTemplateOffers}
      isLoading={templateOffersQuery.isLoading}
    />
  )

  const bookableOffersComponent = (
    <CollectiveOffersCard
      variant={'BOOKABLE'}
      offersToDisplay={bookableOffers}
      hasOffers={hasBookableOffers}
      isLoading={bookableOffersQuery.isLoading}
    />
  )

  if (bookableOffers.length === 0) {
    return (
      <>
        {templateOffersComponent}
        {bookableOffersComponent}
      </>
    )
  }

  return (
    <>
      {bookableOffersComponent}
      {templateOffersComponent}
    </>
  )
}
