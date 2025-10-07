import type React from 'react'
import { createContext, useContext, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { queries, tags } from '@/apiClient/services'
import type {
  CategoryResponseModel,
  GetIndividualOfferWithAddressResponseModel,
  SubcategoryResponseModel,
} from '@/apiClient/v1'
import {
  GET_ACTIVE_VENUE_OFFER_BY_EAN_QUERY_KEY,
  GET_CATEGORIES_QUERY_KEY,
  GET_OFFER_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { isOfferProductBased } from '@/commons/core/Offers/utils/typology'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

export interface IndividualOfferContextValues {
  // TODO (igabriele, 2025-09-09): We should be able to ensure a defined `offer` by setting aside the only case where offer is null (1st creation step).
  offer: GetIndividualOfferWithAddressResponseModel | null
  offerId: number | null
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
  isEvent: boolean | null
  setIsEvent: (isEvent: boolean | null) => void
  /** Real boolean guarded by early `<Splinner />` return while fetching offer data in context provider. */
  hasPublishedOfferWithSameEan: boolean
}

export const IndividualOfferContext =
  createContext<IndividualOfferContextValues>({
    categories: [],
    hasPublishedOfferWithSameEan: false,
    isEvent: null,
    offer: null,
    offerId: null,
    // TODO (igabriele, 2025-08-20): Rename that to `setIsControlledEvent`.
    setIsEvent: () => undefined,
    subCategories: [],
  })

export const useIndividualOfferContext = () => {
  return useContext(IndividualOfferContext)
}

interface IndividualOfferContextProviderProps {
  children: React.ReactNode
}

export const IndividualOfferContextProvider = ({
  children,
}: IndividualOfferContextProviderProps) => {
  const [isControlledEvent, setIsEvent] = useState<boolean | null>(null)
  const { offerId: offerIdAsString } = useParams<{
    offerId: string
  }>()
  const offerId =
    offerIdAsString && offerIdAsString !== 'creation'
      ? Number(offerIdAsString)
      : null

  const SWRConfig = useSWRConfig()

  const navigate = useNavigate()

  const offerQuery = useSWR(
    // TODO (igabriele, 2025-08-18): Use the `mode` via `useOfferWizardMode` hook to keep a single source of truth.
    offerId && offerIdAsString !== 'creation'
      ? queries.getOffer.tag(offerId)
      : null,
    () => api.getOffer(Number(offerId)),
    queries.getOffer.options
  )
  const offer = offerQuery.data

  //  Get the offer on the venue with the same EAN if it exists
  const offerEan = offer?.extraData?.ean
  const offerVenueId = offer?.venue.id
  const isProductBased = isOfferProductBased(offer)
  const publishedOfferWithSameEANQuery = useSWR(
    isProductBased && offerEan && offerVenueId
      ? [GET_ACTIVE_VENUE_OFFER_BY_EAN_QUERY_KEY, offerVenueId, offerEan]
      : null,
    ([, venueId, ean]) => api.getActiveVenueOfferByEan(venueId, ean),
    {
      onError: (error) => {
        if (error.status === 404) {
          return
        }
      },
      shouldRetryOnError: false,
    }
  )

  const categoriesQuery = useSWR(
    [GET_CATEGORIES_QUERY_KEY],
    () => api.getCategories(),
    { fallbackData: { categories: [], subcategories: [] } }
  )

  if (
    offerQuery.isLoading ||
    categoriesQuery.isLoading ||
    publishedOfferWithSameEANQuery.isLoading
  ) {
    return <Spinner />
  }

  //  Only consider a puslished offer that is different from the one we are editing or creating now
  const publishedOfferWithSameEAN =
    offer && publishedOfferWithSameEANQuery.data?.id !== offer.id
      ? publishedOfferWithSameEANQuery.data
      : undefined

  return (
    <IndividualOfferContext.Provider
      value={{
        categories: categoriesQuery.data.categories,
        hasPublishedOfferWithSameEan: Boolean(publishedOfferWithSameEAN),
        isEvent: offer?.isEvent ?? isControlledEvent,
        offer: offer ?? null,
        offerId,
        setIsEvent,
        subCategories: categoriesQuery.data.subcategories,
      }}
    >
      {children}
    </IndividualOfferContext.Provider>
  )
}
