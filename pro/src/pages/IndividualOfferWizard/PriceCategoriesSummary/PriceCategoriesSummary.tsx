/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { PriceCategoriesSummaryScreen } from 'screens/IndividualOffer/PriceCategoriesSummaryScreen/PriceCategoriesSummaryScreen'

export const PriceCategoriesSummary = (): JSX.Element | null => {
  return (
    <IndivualOfferLayout title="Récapitulatif">
      <PriceCategoriesSummaryScreen />
    </IndivualOfferLayout>
  )
}
