/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { useOfferBookingsCount } from 'components/IndividualOfferBreadcrumb/useOfferBookingsCount'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { useOfferWizardMode } from 'hooks'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { StocksSummaryScreen } from 'screens/IndividualOffer/StocksSummaryScreen/StocksSummaryScreen'
import Spinner from 'ui-kit/Spinner/Spinner'

export const StocksSummary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, setOffer } = useIndividualOfferContext()
  const { bookingsCount, isLoading } = useOfferBookingsCount(mode, offer?.id)

  if (offer === null || isLoading) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout
      title="Récapitulatif"
      offer={offer}
      setOffer={setOffer}
      mode={mode}
      bookingsCount={bookingsCount}
    >
      <StocksSummaryScreen />
    </IndivualOfferLayout>
  )
}
