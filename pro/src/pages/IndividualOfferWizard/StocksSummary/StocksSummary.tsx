/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { useOfferWizardMode } from 'hooks'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { StocksSummaryScreen } from 'screens/IndividualOffer/StocksSummaryScreen/StocksSummaryScreen'
import Spinner from 'ui-kit/Spinner/Spinner'

export const StocksSummary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, setOffer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout
      title="Récapitulatif"
      offer={offer}
      setOffer={setOffer}
      mode={mode}
    >
      <StocksSummaryScreen />
    </IndivualOfferLayout>
  )
}
