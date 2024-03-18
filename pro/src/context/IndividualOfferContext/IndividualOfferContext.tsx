import React, { createContext, useContext, useState } from 'react'
import { useLoaderData } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CategoryResponseModel,
  GetIndividualOfferResponseModel,
  GetOffererNameResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import useActiveFeature from 'hooks/useActiveFeature'
import { IndividualOfferWizardLoaderData } from 'pages/IndividualOfferWizard/IndividualOfferWizard'
import Spinner from 'ui-kit/Spinner/Spinner'

export interface IndividualOfferContextValues {
  offerId: number | null
  offer: GetIndividualOfferResponseModel | null
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
  subcategory?: SubcategoryResponseModel
  setSubcategory: (p?: SubcategoryResponseModel) => void
  offererNames: GetOffererNameResponseModel[]
  venueList: VenueListItemResponseModel[]
  offerOfferer?: GetOffererNameResponseModel | null
  showVenuePopin: Record<string, boolean>
}

export const IndividualOfferContext =
  createContext<IndividualOfferContextValues>({
    offerId: null,
    offer: null,
    categories: [],
    subCategories: [],
    offererNames: [],
    venueList: [],
    showVenuePopin: {},
    setSubcategory: () => {},
  })

export const useIndividualOfferContext = () => {
  return useContext(IndividualOfferContext)
}

export interface IndividualOfferContextProviderProps {
  children: React.ReactNode
  isUserAdmin: boolean
  queryOffererId?: string
}

const GET_CATEGORIES_QUERY_KEY = 'getCategories'
const GET_VENUES_QUERY_KEY = 'getVenues'
const GET_OFFERER_NAMES_QUERY_KEY = 'getOffererNames'

export function IndividualOfferContextProvider({
  children,
  isUserAdmin,
  queryOffererId,
}: IndividualOfferContextProviderProps) {
  const { offer } = useLoaderData() as IndividualOfferWizardLoaderData
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const offerer = offer ? offer.venue.managingOfferer : null
  const queryOffererIdAsNumber =
    queryOffererId !== undefined ? Number(queryOffererId) : undefined
  const offererId: number | undefined =
    isUserAdmin && offerer ? offerer.id : queryOffererIdAsNumber

  // We dont want to fetch all venues if admin hasn't selected an offerer
  // TODO: move venuesQuery and offererNamesQuery to the Offer component
  // src/pages/IndividualOfferWizard/Offer/Offer.tsx
  // because it's the only one using this data
  // this can be done once the WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY FF is removed
  // (because venuesQuery is still used here by the old variable showVenuePopin)
  const shouldNotFetchVenues = isUserAdmin && !offererId
  const venuesQuery = useSWR(
    () => (shouldNotFetchVenues ? null : [GET_VENUES_QUERY_KEY, offererId]),
    ([, offererIdParam]) => api.getVenues(null, true, offererIdParam),
    { fallbackData: { venues: [] } }
  )
  const offererNamesQuery = useSWR(
    [GET_OFFERER_NAMES_QUERY_KEY, offererId],
    ([, offererIdParam]) => api.listOfferersNames(null, null, offererIdParam),
    { fallbackData: { offerersNames: [] } }
  )
  const categoriesQuery = useSWR(
    [GET_CATEGORIES_QUERY_KEY],
    () => api.getCategories(),
    { fallbackData: { categories: [], subcategories: [] } }
  )

  const [subcategory, setSubcategory] = useState<SubcategoryResponseModel>()

  const showVenuePopin: Record<string, boolean> =
    !isNewBankDetailsJourneyEnabled
      ? venuesQuery.data.venues.reduce(
          (previousValue, currentValue) => ({
            ...previousValue,
            [currentValue.id]:
              !currentValue.hasCreatedOffer &&
              currentValue.hasMissingReimbursementPoint,
          }),
          {}
        )
      : {}

  if (
    offererNamesQuery.isLoading ||
    categoriesQuery.isLoading ||
    venuesQuery.isLoading
  ) {
    return <Spinner />
  }

  return (
    <IndividualOfferContext.Provider
      value={{
        offerId: offer?.id || null,
        offer,
        categories: categoriesQuery.data.categories,
        subCategories: categoriesQuery.data.subcategories,
        offererNames: offererNamesQuery.data.offerersNames,
        venueList: venuesQuery.data.venues,
        offerOfferer: offerer,
        showVenuePopin: showVenuePopin,
        subcategory,
        setSubcategory,
      }}
    >
      {children}
    </IndividualOfferContext.Provider>
  )
}
