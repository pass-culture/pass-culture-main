import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { SummaryLayout } from 'components/SummaryLayout'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'

export const StocksSummaryScreen = () => {
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return null
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
      aria-label="Modifier les stocks et prix"
    >
      TOUT DOUX
    </SummaryLayout.Section>
  )
}
