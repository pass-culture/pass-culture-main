import React, { createContext, useContext } from 'react'
import { useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CategoryResponseModel,
  GetIndividualOfferResponseModel,
  MusicTypeResponse,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import {
  GET_CATEGORIES_QUERY_KEY,
  GET_MUSIC_TYPES_QUERY_KEY,
  GET_OFFER_QUERY_KEY,
} from 'config/swrQueryKeys'
import Spinner from 'ui-kit/Spinner/Spinner'

export interface IndividualOfferContextValues {
  offerId: number | null
  offer: GetIndividualOfferResponseModel | null
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
  musicTypes: MusicTypeResponse[]
}

export const IndividualOfferContext =
  createContext<IndividualOfferContextValues>({
    offerId: null,
    offer: null,
    categories: [],
    subCategories: [],
    musicTypes: [],
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

  const musicTypesQuery = useSWR(
    GET_MUSIC_TYPES_QUERY_KEY,
    () => api.getMusicTypes(),
    {
      fallbackData: [],
    }
  )

  if (offerQuery.isLoading || categoriesQuery.isLoading) {
    return <Spinner />
  }

  return (
    <IndividualOfferContext.Provider
      value={{
        offerId: offer?.id || null,
        offer: offer ?? null,
        categories: categoriesQuery.data.categories,
        subCategories: categoriesQuery.data.subcategories,
        musicTypes: musicTypesQuery.data,
      }}
    >
      {children}
    </IndividualOfferContext.Provider>
  )
}
