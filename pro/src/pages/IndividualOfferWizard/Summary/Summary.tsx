/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import SummaryScreen from 'screens/IndividualOffer/SummaryScreen/SummaryScreen'
import Spinner from 'ui-kit/Spinner/Spinner'

export const Summary = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()

  const mode = useOfferWizardMode()

  let title: string | undefined = undefined
  if (
    mode === OFFER_WIZARD_MODE.READ_ONLY ||
    mode === OFFER_WIZARD_MODE.EDITION
  ) {
    title = 'Récapitulatif'
  } else {
    title = getTitle(mode)
  }
  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout title={title} offer={offer} mode={mode}>
      <SummaryScreen />
    </IndivualOfferLayout>
  )
}
