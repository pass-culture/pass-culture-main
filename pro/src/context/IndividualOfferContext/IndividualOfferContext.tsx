import React, { createContext, useContext, useEffect, useState } from 'react'
import { useLoaderData, useNavigate } from 'react-router-dom'

import {
  CategoryResponseModel,
  GetIndividualOfferResponseModel,
  GetOffererNameResponseModel,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import { IndividualOfferWizardLoaderData } from 'pages/IndividualOfferWizard/IndividualOfferWizard'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getWizardData } from './adapters'

export interface IndividualOfferContextValues {
  offerId: number | null
  offer: GetIndividualOfferResponseModel | null
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
  subcategory?: SubcategoryResponseModel
  setSubcategory: (p?: SubcategoryResponseModel) => void
  offererNames: GetOffererNameResponseModel[]
  venueList: IndividualOfferVenueItem[]
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
  offerId?: string
  queryOffererId?: string
}

export function IndividualOfferContextProvider({
  children,
  isUserAdmin,
  offerId,
  queryOffererId,
}: IndividualOfferContextProviderProps) {
  const { offer } = useLoaderData() as IndividualOfferWizardLoaderData
  const notify = useNotification()
  const navigate = useNavigate()
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [categories, setCategories] = useState<CategoryResponseModel[]>([])
  const [subCategories, setSubCategories] = useState<
    SubcategoryResponseModel[]
  >([])
  const [subcategory, setSubcategory] = useState<SubcategoryResponseModel>()
  const [offererNames, setOffererNames] = useState<
    GetOffererNameResponseModel[]
  >([])
  const [venueList, setVenueList] = useState<IndividualOfferVenueItem[]>([])
  const [showVenuePopin, setShowVenuePopin] = useState<Record<string, boolean>>(
    {}
  )

  const offerOfferer = offer ? offer.venue.managingOfferer : null

  useEffect(() => {
    async function loadData() {
      const response = await getWizardData({
        offerer: offerOfferer || undefined,
        queryOffererId,
        isAdmin: isUserAdmin,
      })

      if (response.isOk) {
        setCategories(response.payload.categoriesData.categories)
        setSubCategories(response.payload.categoriesData.subCategories)
        setOffererNames(response.payload.offererNames)
        setVenueList(response.payload.venueList)

        if (!isNewBankDetailsJourneyEnabled) {
          const venuesPopinDisplaying: Record<string, boolean> = {}
          response.payload.venueList.forEach((v) => {
            venuesPopinDisplaying[v.id] =
              !v.hasCreatedOffer && v.hasMissingReimbursementPoint
          })
          setShowVenuePopin(venuesPopinDisplaying)
        }
      } else {
        setCategories([])
        setSubCategories([])
        setOffererNames([])
        setVenueList([])
        navigate('/accueil')
        notify.error(GET_DATA_ERROR_MESSAGE)
      }
      setIsLoading(false)
    }
    if (!offerId || offer !== null) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      loadData()
    }
  }, [offerId, offerOfferer])

  if (isLoading === true) {
    return <Spinner />
  }

  return (
    <IndividualOfferContext.Provider
      value={{
        offerId: offer?.id || null,
        offer,
        categories,
        subCategories,
        offererNames,
        venueList,
        offerOfferer,
        showVenuePopin: showVenuePopin,
        subcategory,
        setSubcategory,
      }}
    >
      {children}
    </IndividualOfferContext.Provider>
  )
}
