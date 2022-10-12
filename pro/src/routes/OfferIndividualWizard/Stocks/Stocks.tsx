import React from 'react'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { IOfferIndividual } from 'core/Offers/types'
import { useNavigate } from 'hooks'
import {
  StocksThing as StocksThingScreen,
  Template as WizardTemplate,
} from 'screens/OfferIndividual'

const Stocks = (): JSX.Element | null => {
  const { offer } = useOfferIndividualContext()
  const navigate = useNavigate()

  if (offer === null) {
    navigate('/offer/creation/individuelle/informations')
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
