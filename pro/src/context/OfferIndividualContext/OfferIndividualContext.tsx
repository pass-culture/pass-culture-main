import React, { createContext, useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { OffererName } from 'core/Offerers/types'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import {
  OfferCategory,
  OfferIndividual,
  OfferSubCategory,
} from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { OfferIndividualVenue } from 'core/Venue/types'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getWizardData } from './adapters'

export interface OfferIndividualContextValues {
  offerId: number | null
  offer: OfferIndividual | null
  setOffer: ((offer: OfferIndividual | null) => void) | null
  categories: OfferCategory[]
  subCategories: OfferSubCategory[]
  offererNames: OffererName[]
  venueList: OfferIndividualVenue[]
  shouldTrack: boolean
  setShouldTrack: (p: boolean) => void
  venueId?: number | undefined
  offerOfferer?: OffererName | null
  showVenuePopin: Record<string, boolean>
}

export const OfferIndividualContext =
  createContext<OfferIndividualContextValues>({
    offerId: null,
    offer: null,
    setOffer: null,
    categories: [],
    subCategories: [],
    offererNames: [],
    venueList: [],
    shouldTrack: true,
    setShouldTrack: () => {},
    showVenuePopin: {},
  })

export const useOfferIndividualContext = () => {
  return useContext(OfferIndividualContext)
}

interface OfferIndividualContextProviderProps {
  children: React.ReactNode
  isUserAdmin: boolean
  offerId?: string
  queryOffererId?: string
}

export function OfferIndividualContextProvider({
  children,
  isUserAdmin,
  offerId,
  queryOffererId,
}: OfferIndividualContextProviderProps) {
  const homePath = '/accueil'
  const notify = useNotification()
  const navigate = useNavigate()

  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [shouldTrack, setShouldTrack] = useState<boolean>(true)
  const [offerOfferer, setOfferOfferer] = useState<OffererName | null>(null)
  const [venueId, setVenueId] = useState<number>()

  const [offer, setOfferState] = useState<OfferIndividual | null>(null)
  const [categories, setCategories] = useState<OfferCategory[]>([])
  const [subCategories, setSubCategories] = useState<OfferSubCategory[]>([])
  const [offererNames, setOffererNames] = useState<OffererName[]>([])
  const [venueList, setVenueList] = useState<OfferIndividualVenue[]>([])
  const [showVenuePopin, setShowVenuePopin] = useState<Record<string, boolean>>(
    {}
  )

  const setOffer = (offer: OfferIndividual | null) => {
    setOfferState(offer)
    setOfferOfferer(
      offer
        ? {
            nonHumanizedId: offer.venue.offerer.nonHumanizedId,
            name: offer.venue.offerer.name,
          }
        : null
    )
  }

  useEffect(() => {
    async function loadOffer() {
      const response = await getOfferIndividualAdapter(Number(offerId))
      if (response.isOk) {
        setOffer(response.payload)
        setVenueId(response.payload.venueId)
      } else {
        navigate(homePath)
        notify.error(
          'Une erreur est survenue lors de la récupération de votre offre'
        )
      }
    }
    offerId ? loadOffer() : setOffer(null)
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
        response.payload.venueList.forEach(v => {
          venuesPopinDisplaying[v.nonHumanizedId] =
            !v.hasCreatedOffer && v.hasMissingReimbursementPoint
        })
        setShowVenuePopin(venuesPopinDisplaying)
      } else {
        setCategories([])
        setSubCategories([])
        setOffererNames([])
        setVenueList([])
        navigate(homePath)
        notify.error(GET_DATA_ERROR_MESSAGE)
      }
      setIsLoading(false)
    }
    if (!offerId || offer !== null) {
      loadData()
    }
  }, [offerId, offerOfferer])

  if (isLoading === true) {
    return <Spinner />
  }

  return (
    <OfferIndividualContext.Provider
      value={{
        offerId: offer?.nonHumanizedId || null,
        offer,
        setOffer,
        categories,
        subCategories,
        offererNames,
        venueList,
        shouldTrack,
        setShouldTrack,
        venueId,
        offerOfferer,
        showVenuePopin: showVenuePopin,
      }}
    >
      {children}
    </OfferIndividualContext.Provider>
  )
}
