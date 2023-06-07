import React, { createContext, useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { TOffererName } from 'core/Offerers/types'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import {
  IOfferCategory,
  IOfferIndividual,
  IOfferSubCategory,
} from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getWizardData } from './adapters'

export interface IOfferIndividualContext {
  offerId: number | null
  offer: IOfferIndividual | null
  setOffer: ((offer: IOfferIndividual | null) => void) | null
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  shouldTrack: boolean
  setShouldTrack: (p: boolean) => void
  venueId?: number | undefined
  offerOfferer?: TOffererName | null
  showVenuePopin: Record<string, boolean>
}

export const OfferIndividualContext = createContext<IOfferIndividualContext>({
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

interface IOfferIndividualContextProviderProps {
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
}: IOfferIndividualContextProviderProps) {
  const homePath = '/accueil'
  const notify = useNotification()
  const navigate = useNavigate()

  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [shouldTrack, setShouldTrack] = useState<boolean>(true)
  const [offerOfferer, setOfferOfferer] = useState<TOffererName | null>(null)
  const [venueId, setVenueId] = useState<number>()

  const [offer, setOfferState] = useState<IOfferIndividual | null>(null)
  const [categories, setCategories] = useState<IOfferCategory[]>([])
  const [subCategories, setSubCategories] = useState<IOfferSubCategory[]>([])
  const [offererNames, setOffererNames] = useState<TOffererName[]>([])
  const [venueList, setVenueList] = useState<TOfferIndividualVenue[]>([])
  const [showVenuePopin, setShowVenuePopin] = useState<Record<string, boolean>>(
    {}
  )

  const setOffer = (offer: IOfferIndividual | null) => {
    setOfferState(offer)
    setOfferOfferer(
      offer
        ? {
            id: offer.venue.offerer.id,
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
          venuesPopinDisplaying[v.id] =
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
