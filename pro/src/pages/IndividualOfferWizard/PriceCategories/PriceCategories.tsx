import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { PriceCategories as PriceCategoriesScreen } from 'screens/IndividualOffer/PriceCategories/PriceCategories'

export const PriceCategories = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()

  // Offer might be null: when we submit Informations form, we setOffer with the
  // submited payload. Due to React 18 render batching behavior and react-router
  // implementation, this component can be rendered before the offer is set in the
  // offer individual context
  if (offer === null) {
    return null
  }

  return (
    <IndivualOfferLayout>
      <PriceCategoriesScreen offer={offer} />
    </IndivualOfferLayout>
  )
}
