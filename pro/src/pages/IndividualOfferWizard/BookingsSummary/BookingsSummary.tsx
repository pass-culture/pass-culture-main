/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import useOfferWizardMode from 'hooks/useOfferWizardMode'
import { BookingsSummaryScreen } from 'screens/IndividualOffer/BookingsSummary/BookingsSummary'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import Spinner from 'ui-kit/Spinner/Spinner'

export const BookingsSummary = (): JSX.Element | null => {
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
      <BookingsSummaryScreen offer={offer} />
    </IndivualOfferLayout>
  )
}
