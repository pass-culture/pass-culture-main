import type React from 'react'
import { createContext, useContext, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type {
  CategoryResponseModel,
  GetActiveEANOfferResponseModel,
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
  offer: GetIndividualOfferWithAddressResponseModel | null
  // TODO (igabriele, 2025-08-19): Remove the `?` in another PR.
  offerId?: number | null
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
  isEvent: boolean | null
  setIsEvent: (isEvent: boolean | null) => void
  // Both isAccessibilityFilled and setIsAccessibilityFilled are
  // used as a workaround to make the form context sync with the offer context
  // so the stepper can be updated depending on form changes.
  isAccessibilityFilled: boolean
  setIsAccessibilityFilled: (isAccessibilityFilled: boolean) => void
  /** Real boolean guarded by early `<Splinner />` return while fetching offer data in context provider. */
  // TODO (igabriele, 2025-08-19): Remove the `?` in another PR.
  hasPublishedOfferWithSameEan?: boolean
  /** @deprecated Use `hasPublishedOfferWithSameEan` instead. */
  publishedOfferWithSameEAN?: GetActiveEANOfferResponseModel
}

export const IndividualOfferContext =
  createContext<IndividualOfferContextValues>({
    categories: [],
    hasPublishedOfferWithSameEan: false,
    isAccessibilityFilled: true,
    isEvent: null,
    offer: null,
    offerId: null,
    setIsAccessibilityFilled: () => undefined,
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
  const [isAccessibilityFilled, setIsAccessibilityFilled] = useState(true)
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
      ? [GET_OFFER_QUERY_KEY, Number(offerId)]
      : null,
    ([, offerIdParam]) => api.getOffer(offerIdParam),
    {
      onError: (error, key) => {
        if (error.status === 404) {
          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          navigate('/404', { state: { from: 'offer' } })
          return
        }
        SWRConfig.onError(error, key, SWRConfig)
      },
    }
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
        isAccessibilityFilled,
        isEvent: offer?.isEvent ?? isControlledEvent,
        offer: offer ?? null,
        offerId,
        publishedOfferWithSameEAN,
        setIsAccessibilityFilled,
        setIsEvent,
        subCategories: categoriesQuery.data.subcategories,
      }}
    >
      {children}
    </IndividualOfferContext.Provider>
  )
}
