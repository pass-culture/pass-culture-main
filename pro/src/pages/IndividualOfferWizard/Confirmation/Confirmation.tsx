import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { useOfferWizardMode } from 'hooks'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import IndividualOfferConfirmationScreen from 'screens/IndividualOfferConfirmationScreen/IndividualOfferConfirmationScreen'
import Spinner from 'ui-kit/Spinner/Spinner'

const Confirmation = (): JSX.Element => {
  const mode = useOfferWizardMode()
  const { offer, setOffer } = useIndividualOfferContext()

  return (
    <>
      <Spinner isLoading={offer === null} />
      {offer !== null && (
        <IndivualOfferLayout
          withStepper={false}
          offer={offer}
          setOffer={setOffer}
          title={getTitle(mode)}
          mode={mode}
        >
          <IndividualOfferConfirmationScreen offer={offer} />
        </IndivualOfferLayout>
      )}
    </>
  )
}

export default Confirmation
