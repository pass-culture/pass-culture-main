import React from 'react'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { IOfferIndividual } from 'core/Offers/types'
import { Template as WizardTemplate } from 'screens/OfferIndividual'
import { OfferIndividualConfirmation as OfferIndividualConfirmationScreen } from 'screens/OfferIndividualConfirmation'

const Confirmation = (): JSX.Element => {
  const { offer } = useOfferIndividualContext()
  // FIXME : we should not need  as IOfferIndividual cause parent route would redirect on offer loading error
  return (
    <WizardTemplate withStepper={false} withStatus={false} withBanner={false}>
      <OfferIndividualConfirmationScreen offer={offer as IOfferIndividual} />
    </WizardTemplate>
  )
}

export default Confirmation
