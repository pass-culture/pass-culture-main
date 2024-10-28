/* istanbul ignore file */
import React from 'react'

import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { ActionBar } from 'components/IndividualOffer/ActionBar/ActionBar'
import { IndivualOfferLayout } from 'components/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { IndividualOfferBooklngsSummaryScreen } from './components/IndividualOfferBooklngsSummaryScreen'

const IndividualOfferBookings = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      <IndividualOfferBooklngsSummaryScreen offer={offer} />
      <ActionBar step={OFFER_WIZARD_STEP_IDS.SUMMARY} isDisabled={false} />
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferBookings
