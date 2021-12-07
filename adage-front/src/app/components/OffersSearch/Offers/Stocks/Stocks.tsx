import React from 'react'

import { StockType } from 'utils/types'

import { Stock } from './Stock'

export const Stocks = ({
  canPrebookOffers,
  stocks,
  venuePostalCode,
}: {
  canPrebookOffers: boolean
  stocks: StockType[]
  venuePostalCode: string
}): JSX.Element => {
  return (
    <ul className="stocks">
      {stocks.map(
        (stock: StockType) =>
          stock.isBookable && (
            <Stock
              canPrebookOffers={canPrebookOffers}
              key={stock.id}
              stock={stock}
              venuePostalCode={venuePostalCode}
            />
          )
      )}
    </ul>
  )
}
