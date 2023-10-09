import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { useOfferWizardMode } from 'hooks'
import IndividualOfferLayout from 'screens/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndividualOfferLayout/utils/getTitle'
import IndividualOfferConfirmationScreen from 'screens/IndividualOfferConfirmationScreen/IndividualOfferConfirmationScreen'
import Spinner from 'ui-kit/Spinner/Spinner'

const Confirmation = (): JSX.Element => {
  const mode = useOfferWizardMode()
  const { offer, setOffer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout
      withStepper={false}
      offer={offer}
      setOffer={setOffer}
      title={getTitle(mode)}
      mode={mode}
    >
      <IndividualOfferConfirmationScreen offer={offer} />
    </IndividualOfferLayout>
  )
}

export default Confirmation
