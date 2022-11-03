import React, { createContext, useContext, useEffect, useState } from 'react'

import { TOffererName } from 'core/Offerers/types'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import {
  IOfferCategory,
  IOfferIndividual,
  IOfferSubCategory,
} from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { useHomePath, useNavigate } from 'hooks'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getWizardData } from './adapters'

export interface IOfferIndividualContext {
  offerId: string | null
  offer: IOfferIndividual | null
  setOffer: ((offer: IOfferIndividual | null) => void) | null
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
}

export const OfferIndividualContext = createContext<IOfferIndividualContext>({
  offerId: null,
  offer: null,
  setOffer: null,
  categories: [],
  subCategories: [],
  offererNames: [],
  venueList: [],
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
  const homePath = useHomePath()
  const notify = useNotification()
  const navigate = useNavigate()

  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [offerOfferer, setOfferOfferer] = useState<TOffererName | null>(null)

  const [offer, setOfferState] = useState<IOfferIndividual | null>(null)
  const [categories, setCategories] = useState<IOfferCategory[]>([])
  const [subCategories, setSubCategories] = useState<IOfferSubCategory[]>([])
  const [offererNames, setOffererNames] = useState<TOffererName[]>([])
  const [venueList, setVenueList] = useState<TOfferIndividualVenue[]>([])

  const setOffer = (offer: IOfferIndividual | null) => {
    setOfferState(offer)
    setOfferOfferer(
      offer
        ? {
            id: offer.venue.offerer.id,
            name: offer.venue.offerer.name,
          }
        : null
    )
  }

  useEffect(() => {
    async function loadOffer() {
      const response = await getOfferIndividualAdapter(offerId)
      if (response.isOk) {
        setOffer(response.payload)
      } else {
        notify.error(
          'Une erreur est survenue lors de la récupération de votre offre'
        )
        navigate(homePath)
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
      } else {
        setCategories([])
        setSubCategories([])
        setOffererNames([])
        setVenueList([])
        notify.error(GET_DATA_ERROR_MESSAGE)
        navigate(homePath)
      }
      setIsLoading(false)
    }
    ;(!offerId || offer !== null) && loadData()
  }, [offerId, offerOfferer])

  if (isLoading === true) return <Spinner />

  return (
    <OfferIndividualContext.Provider
      value={{
        offerId: offer?.id || null,
        offer,
        setOffer,
        categories,
        subCategories,
        offererNames,
        venueList,
      }}
    >
      {children}
    </OfferIndividualContext.Provider>
  )
}
