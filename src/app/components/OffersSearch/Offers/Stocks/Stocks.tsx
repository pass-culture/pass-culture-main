import React from "react"

import { StockType } from "utils/types"

import { Stock } from "./Stock"

export const Stocks = ({
  stocks,
  venuePostalCode,
}: {
  stocks: StockType[];
  venuePostalCode: string;
}): JSX.Element => {
  return (
    <ul className="stocks">
      {stocks.map((stock: StockType) => (
        <Stock
          key={stock.id}
          stock={stock}
          venuePostalCode={venuePostalCode}
        />
      ))}
    </ul>
  )
}
