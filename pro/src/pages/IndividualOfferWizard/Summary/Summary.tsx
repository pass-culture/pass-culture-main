/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { useOfferBookingsCount } from 'components/IndividualOfferBreadcrumb/useOfferBookingsCount'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import SummaryScreen from 'screens/IndividualOffer/SummaryScreen/SummaryScreen'
import Spinner from 'ui-kit/Spinner/Spinner'

export const Summary = (): JSX.Element | null => {
  const { offer, setOffer } = useIndividualOfferContext()
  const mode = useOfferWizardMode()
  const { bookingsCount, isLoading } = useOfferBookingsCount(mode, offer?.id)

  let title: string | undefined = undefined
  if (
    mode === OFFER_WIZARD_MODE.READ_ONLY ||
    mode === OFFER_WIZARD_MODE.EDITION
  ) {
    title = 'Récapitulatif'
  } else {
    title = getTitle(mode)
  }
  if (offer === null || isLoading) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout
      title={title}
      offer={offer}
      setOffer={setOffer}
      mode={mode}
      bookingsCount={bookingsCount}
    >
      <SummaryScreen />
    </IndivualOfferLayout>
  )
}
