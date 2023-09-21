/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { Template as WizardTemplate } from 'screens/IndividualOffer'
import { StocksSummary as StocksSummaryScreen } from 'screens/IndividualOffer/StocksSummary/StocksSummary'

export const StocksSummary = (): JSX.Element | null => {
  return (
    <WizardTemplate title="Récapitulatif">
      <StocksSummaryScreen />
    </WizardTemplate>
  )
}
