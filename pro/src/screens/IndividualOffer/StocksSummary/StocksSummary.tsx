import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { SummaryLayout } from 'components/SummaryLayout'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'

export const StocksSummary = () => {
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return null
  }
  const mode = useOfferWizardMode()
  const { logEvent } = useAnalytics()

  const logEditEvent = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.SUMMARY,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft:
        mode === OFFER_WIZARD_MODE.CREATION || mode === OFFER_WIZARD_MODE.DRAFT,
      offerId: offer.id,
    })
  }

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode: OFFER_WIZARD_MODE.EDITION,
  })

  return (
    <SummaryLayout.Section
      title={offer.isEvent ? 'Dates et capacité' : 'Stocks et prix'}
      editLink={editLink}
      onLinkClick={logEditEvent}
      aria-label="Modifier les stocks et prix"
    >
      TOUT DOUX
    </SummaryLayout.Section>
  )
}
