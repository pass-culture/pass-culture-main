import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { IndividualOffer } from 'core/Offers/types'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import IndividualOfferConfirmationScreen from 'screens/IndividualOfferConfirmationScreen/IndividualOfferConfirmationScreen'

const Confirmation = (): JSX.Element => {
  const { offer } = useIndividualOfferContext()
  // FIXME : we should not need  as IndividualOffer cause parent route would redirect on offer loading error
  return (
    <IndivualOfferLayout withStepper={false}>
      <IndividualOfferConfirmationScreen offer={offer as IndividualOffer} />
    </IndivualOfferLayout>
  )
}

export default Confirmation
