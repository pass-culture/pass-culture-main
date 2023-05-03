import React from 'react'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  PriceCategories as PriceCategoriesScreen,
  Template as WizardTemplate,
} from 'screens/OfferIndividual'

const PriceCategories = (): JSX.Element | null => {
  const { offer } = useOfferIndividualContext()

  // Offer might be null: when we submit Informations form, we setOffer with the
  // submited payload. Due to React 18 render batching behavior and react-router
  // implementation, this component can be rendered before the offer is set in the
  // offer individual context
  if (offer === null) {
    return null
  }

  return (
    <WizardTemplate>
      <PriceCategoriesScreen offer={offer} />
    </WizardTemplate>
  )
}

export default PriceCategories
