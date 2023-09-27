import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import IndividualOfferConfirmationScreen from 'screens/IndividualOfferConfirmationScreen/IndividualOfferConfirmationScreen'
import Spinner from 'ui-kit/Spinner/Spinner'

const Confirmation = (): JSX.Element => {
  const { offer, setOffer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout withStepper={false} offer={offer} setOffer={setOffer}>
      <IndividualOfferConfirmationScreen offer={offer} />
    </IndivualOfferLayout>
  )
}

export default Confirmation
