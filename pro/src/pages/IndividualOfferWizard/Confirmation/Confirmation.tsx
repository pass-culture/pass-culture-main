import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { IndividualOffer } from 'core/Offers/types'
import { Template as WizardTemplate } from 'screens/IndividualOffer'
import { IndividualOfferConfirmation as IndividualOfferConfirmationScreen } from 'screens/IndividualOfferConfirmation'

const Confirmation = (): JSX.Element => {
  const { offer } = useIndividualOfferContext()
  // FIXME : we should not need  as IndividualOffer cause parent route would redirect on offer loading error
  return (
    <WizardTemplate withStepper={false} withStatus={false} withBanner={false}>
      <IndividualOfferConfirmationScreen offer={offer as IndividualOffer} />
    </WizardTemplate>
  )
}

export default Confirmation
