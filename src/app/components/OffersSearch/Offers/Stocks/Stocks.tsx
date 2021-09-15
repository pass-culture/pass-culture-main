import React from "react"

import { Notification } from "app/components/Layout/Notification/Notification"
import { StockType } from "utils/types"

import { Stock } from "./Stock"

export const Stocks = ({
  canPrebookOffers,
  notify,
  stocks,
  venuePostalCode,
}: {
  canPrebookOffers: boolean;
  notify: (notification: Notification) => void;
  stocks: StockType[];
  venuePostalCode: string;
}): JSX.Element => {
  return (
    <ul className="stocks">
      {stocks.map(
        (stock: StockType) =>
          stock.isBookable && (
            <Stock
              canPrebookOffers={canPrebookOffers}
              key={stock.id}
              notify={notify}
              stock={stock}
              venuePostalCode={venuePostalCode}
            />
          )
      )}
    </ul>
  )
}
