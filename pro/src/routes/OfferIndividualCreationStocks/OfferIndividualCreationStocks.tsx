import React from 'react'

import { IOfferIndividual } from 'core/Offers/types'
import { Stocks as StocksScreen } from 'screens/OfferIndividual/Stocks'

interface IOfferIndividualCreationInformationsProps {
  offer: IOfferIndividual
}

const OfferIndividualCreationStocks = ({
  offer,
}: IOfferIndividualCreationInformationsProps): JSX.Element | null => {
  return (
    <div>
      <StocksScreen offer={offer} />
    </div>
  )
}

export default OfferIndividualCreationStocks
