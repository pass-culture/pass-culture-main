import React, { createContext, useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { OffererName } from 'core/Offerers/types'
import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { IndividualOffer } from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getWizardData } from './adapters'

export interface IndividualOfferContextValues {
  offerId: number | null
  offer: IndividualOffer | null
  setOffer: ((offer: IndividualOffer | null) => void) | null
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
  subcategory?: SubcategoryResponseModel
  setSubcategory: (p?: SubcategoryResponseModel) => void
  offererNames: OffererName[]
  venueList: IndividualOfferVenueItem[]
  venueId?: number | undefined
  offerOfferer?: OffererName | null
  showVenuePopin: Record<string, boolean>
}

export const IndividualOfferContext =
  createContext<IndividualOfferContextValues>({
    offerId: null,
    offer: null,
    setOffer: null,
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

interface IndividualOfferContextProviderProps {
  children: React.ReactNode
  isUserAdmin: boolean
  offerId?: string
  queryOffererId?: string
  querySubcategoryId?: string
}

export function IndividualOfferContextProvider({
  children,
  isUserAdmin,
  offerId,
  queryOffererId,
  querySubcategoryId,
}: IndividualOfferContextProviderProps) {
  const notify = useNotification()
  const navigate = useNavigate()

  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [offerOfferer, setOfferOfferer] = useState<OffererName | null>(null)
  const [venueId, setVenueId] = useState<number>()

  const [offer, setOfferState] = useState<IndividualOffer | null>(null)
  const [categories, setCategories] = useState<CategoryResponseModel[]>([])
  const [subCategories, setSubCategories] = useState<
    SubcategoryResponseModel[]
  >([])
  const [subcategory, setSubcategory] = useState<SubcategoryResponseModel>()
  const [offererNames, setOffererNames] = useState<OffererName[]>([])
  const [venueList, setVenueList] = useState<IndividualOfferVenueItem[]>([])
  const [showVenuePopin, setShowVenuePopin] = useState<Record<string, boolean>>(
    {}
  )

  const setOffer = (offer: IndividualOffer | null) => {
    setOfferState(offer)
    setOfferOfferer(offer ? offer.venue.managingOfferer : null)
  }

  useEffect(() => {
    async function loadOffer() {
      const response = await getIndividualOfferAdapter(Number(offerId))
      if (response.isOk) {
        setOffer(response.payload)
        setVenueId(response.payload.venueId)
      } else {
        navigate('/accueil')
        notify.error(
          'Une erreur est survenue lors de la récupération de votre offre'
        )
      }
    }
    if (offerId) {
      void loadOffer()
    } else {
      setOffer(null)
    }
  }, [offerId])

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
        const venuesPopinDisplaying: Record<string, boolean> = {}
        response.payload.venueList.forEach((v) => {
          venuesPopinDisplaying[v.id] =
            !v.hasCreatedOffer && v.hasMissingReimbursementPoint
        })
        setShowVenuePopin(venuesPopinDisplaying)
        setSubcategory(
          response.payload.categoriesData.subCategories.find(
            (s) => s.id === querySubcategoryId
          )
        )
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
      void loadData()
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
        setOffer,
        categories,
        subCategories,
        offererNames,
        venueList,
        venueId,
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
