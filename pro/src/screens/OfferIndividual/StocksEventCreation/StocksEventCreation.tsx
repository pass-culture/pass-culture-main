import React from 'react'

import { IOfferIndividual } from 'core/Offers/types'

export interface IStocksEventCreationProps {
  offer: IOfferIndividual
}

export const StocksEventCreation = ({
  offer,
}: IStocksEventCreationProps): JSX.Element => {
  return <div>Récurrence</div>
}
