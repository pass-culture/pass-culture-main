import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'

import { PriceCategoriesSection } from '../SummaryScreen/PriceCategoriesSection/PriceCategoriesSection'

export const PriceCategoriesSummaryScreen = () => {
  const { offer, subCategories } = useIndividualOfferContext()

  if (offer === null) {
    return null
  }
  const canBeDuo = subCategories.find(
    subCategory => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  return <PriceCategoriesSection offer={offer} canBeDuo={canBeDuo} />
}
