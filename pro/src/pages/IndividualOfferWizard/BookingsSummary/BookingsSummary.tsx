/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { Template as WizardTemplate } from 'screens/IndividualOffer'
import { BookingsSummaryScreen } from 'screens/IndividualOffer/BookingsSummary/BookingsSummary'

export const BookingsSummary = (): JSX.Element | null => {
  return (
    <WizardTemplate title="Récapitulatif">
      <BookingsSummaryScreen />
    </WizardTemplate>
  )
}
