import React, { createContext, useContext, useState } from 'react'
import { useParams } from 'react-router'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CategoryResponseModel,
  GetIndividualOfferWithAddressResponseModel,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import {
  GET_CATEGORIES_QUERY_KEY,
  GET_OFFER_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export interface IndividualOfferContextValues {
  offer: GetIndividualOfferWithAddressResponseModel | null
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
  isEvent: boolean | null
  setIsEvent: (isEvent: boolean | null) => void
}

export const IndividualOfferContext =
  createContext<IndividualOfferContextValues>({
    offer: null,
    categories: [],
    subCategories: [],
    isEvent: null,
    setIsEvent: () => {},
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
  const [isEvent, setIsEvent] = useState<boolean | null>(null)
  const { offerId } = useParams<{
    offerId: string
  }>()

  const offerQuery = useSWR(
    offerId && offerId !== 'creation'
      ? [GET_OFFER_QUERY_KEY, Number(offerId)]
      : null,
    ([, offerIdParam]) => api.getOffer(offerIdParam)
  )
  const offer = offerQuery.data

  const categoriesQuery = useSWR(
    [GET_CATEGORIES_QUERY_KEY],
    () => api.getCategories(),
    { fallbackData: { categories: [], subcategories: [] } }
  )

  if (offerQuery.isLoading || categoriesQuery.isLoading) {
    return <Spinner />
  }

  return (
    <IndividualOfferContext.Provider
      value={{
        offer: offer ?? null,
        isEvent,
        categories: categoriesQuery.data.categories,
        subCategories: categoriesQuery.data.subcategories,
        setIsEvent,
      }}
    >
      {children}
    </IndividualOfferContext.Provider>
  )
}
