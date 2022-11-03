import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate } from 'hooks'
import {
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

  // FIXME : we should not need  as IOfferIndividual cause parent route would redirect on offer loading error
  return (
    <WizardTemplate>
      {offer.isEvent ? (
        <div>TODO Stock Event screen</div>
      ) : (
        <StocksThingScreen offer={offer as IOfferIndividual} />
      )}
    </WizardTemplate>
  )
}

export default Stocks
