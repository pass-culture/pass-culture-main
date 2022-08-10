import React, { createContext, useContext } from 'react'

import { TOffererName } from 'core/Offerers/types'
import {
  IOfferCategory,
  IOfferIndividual,
  IOfferSubCategory,
} from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'

export interface IOfferIndividualContext {
  offerId: string | null
  offer: IOfferIndividual | null
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  reloadOffer: () => void
}

export const OfferIndividualContext = createContext<IOfferIndividualContext>({
  offerId: null,
  offer: null,
  categories: [],
  subCategories: [],
  offererNames: [],
  venueList: [],
  reloadOffer: () => {},
})

export const useOfferIndividualContext = () => {
  return useContext(OfferIndividualContext)
}

interface IOfferIndividualContextProviderProps {
  children: React.ReactNode
  initialContext: IOfferIndividualContext
}

export function OfferIndividualContextProvider({
  children,
  initialContext,
}: IOfferIndividualContextProviderProps) {
  return (
    <OfferIndividualContext.Provider value={initialContext}>
      {children}
    </OfferIndividualContext.Provider>
  )
}
