/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import {
  Summary as SummaryScreen,
  Template as WizardTemplate,
} from 'screens/IndividualOffer'

export const Summary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()

  let title: string | undefined = undefined
  if (
    mode === OFFER_WIZARD_MODE.READ_ONLY ||
    mode === OFFER_WIZARD_MODE.EDITION
  ) {
    title = 'Récapitulatif'
  }
  return (
    <WizardTemplate title={title}>
      <SummaryScreen />
    </WizardTemplate>
  )
}
