/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { OFFER_WIZARD_MODE } from 'core/Offers'
import { useOfferWizardMode } from 'hooks'
import {
  Summary as SummaryScreen,
  Template as WizardTemplate,
} from 'screens/OfferIndividual'

const Summary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()

  let title: string | undefined = undefined
  if (mode === OFFER_WIZARD_MODE.EDITION) {
    title = 'Récapitulatif'
  }
  return (
    <WizardTemplate
      title={title}
      withStepper={mode !== OFFER_WIZARD_MODE.EDITION}
    >
      <SummaryScreen />
    </WizardTemplate>
  )
}

export default Summary
