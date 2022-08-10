import React from 'react'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { IOfferIndividual } from 'core/Offers/types'
import {
  Stocks as StocksScreen,
  Template as WizardTemplate,
} from 'screens/OfferIndividual'

const Stocks = (): JSX.Element | null => {
  const { offer } = useOfferIndividualContext()

  // FIXME : we should not need  as IOfferIndividual cause parent route would redirect on offer loading error
  return (
    <WizardTemplate>
      <StocksScreen offer={offer as IOfferIndividual} />
    </WizardTemplate>
  )
}

export default Stocks
