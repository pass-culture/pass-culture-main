/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { StocksSummaryScreen } from 'screens/IndividualOffer/StocksSummaryScreen/StocksSummaryScreen'

export const StocksSummary = (): JSX.Element | null => {
  return (
    <IndivualOfferLayout title="Récapitulatif">
      <StocksSummaryScreen />
    </IndivualOfferLayout>
  )
}
