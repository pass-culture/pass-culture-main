import React from 'react'
import { useNavigate } from 'react-router-dom-v5-compat'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import {
  StocksEventEdition,
  StocksThing,
  Template,
} from 'screens/OfferIndividual'
import { StocksEventCreation } from 'screens/OfferIndividual/StocksEventCreation/StocksEventCreation'

const Stocks = (): JSX.Element | null => {
  const { offer } = useOfferIndividualContext()
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const isRecurrenceActive = useActiveFeature('WIP_RECURRENCE')

  // if we've no offer, we are redirect from parent route.
  /* istanbul ignore next: DEBT, TO FIX */
  if (offer === null) {
    navigate(
      getOfferIndividualUrl({
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode: OFFER_WIZARD_MODE.CREATION,
      })
    )
    return null
  }

  return (
    <Template>
      {offer.isEvent ? (
        isRecurrenceActive && mode !== OFFER_WIZARD_MODE.EDITION ? (
          <StocksEventCreation offer={offer} />
        ) : (
          <StocksEventEdition offer={offer} />
        )
      ) : (
        <StocksThing offer={offer} />
      )}
    </Template>
  )
}

export default Stocks
