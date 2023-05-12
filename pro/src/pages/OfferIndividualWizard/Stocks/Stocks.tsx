import React from 'react'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { useOfferWizardMode } from 'hooks'
import {
  StocksEventEdition,
  StocksThing,
  Template,
} from 'screens/OfferIndividual'
import { StocksEventCreation } from 'screens/OfferIndividual/StocksEventCreation/StocksEventCreation'
import Spinner from 'ui-kit/Spinner/Spinner'

const Stocks = (): JSX.Element | null => {
  const { offer } = useOfferIndividualContext()
  const mode = useOfferWizardMode()

  // Here we display a spinner because when the router transitions from
  // Informations form to Stocks form the setOffer after the submit is not
  // propagated yet so there is a quick moment where the offer is null.
  // This is a temporary fix until we use a better pattern than the OfferIndividualWizard
  // to share the offer context
  if (offer === null) {
    return <Spinner />
  }

  return (
    <Template>
      {offer.isEvent ? (
        mode !== OFFER_WIZARD_MODE.EDITION ? (
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
