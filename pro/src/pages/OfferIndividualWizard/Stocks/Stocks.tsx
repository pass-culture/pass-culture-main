import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate } from 'hooks'
import {
  StocksEvent as StocksEventScreen,
  StocksThing as StocksThingScreen,
  Template as WizardTemplate,
} from 'screens/OfferIndividual'

const Stocks = (): JSX.Element | null => {
  const { offer } = useOfferIndividualContext()
  const navigate = useNavigate()

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
    <WizardTemplate>
      {offer.isEvent ? (
        <StocksEventScreen offer={offer} />
      ) : (
        <StocksThingScreen offer={offer} />
      )}
    </WizardTemplate>
  )
}

export default Stocks
