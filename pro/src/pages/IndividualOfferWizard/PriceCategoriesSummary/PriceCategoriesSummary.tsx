/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { Template as WizardTemplate } from 'screens/IndividualOffer'
import { PriceCategoriesSummaryScreen } from 'screens/IndividualOffer/PriceCategoriesSummary/PriceCategoriesSummary'

export const PriceCategoriesSummary = (): JSX.Element | null => {
  return (
    <WizardTemplate title="Récapitulatif">
      <PriceCategoriesSummaryScreen />
    </WizardTemplate>
  )
}
