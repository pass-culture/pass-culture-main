import React from "react"

import {
  FORMAT_DD_MM_YYYY_HH_mm,
  toISOStringWithoutMilliseconds,
} from "utils/date"
import { formatLocalTimeDateString } from "utils/timezone"
import { StockType } from "utils/types"

const printStockInformation = (
  stock: StockType,
  venueDepartmentCode: string
): string => {
  const stockBeginningDate = new Date(stock.beginningDatetime)
  const stockBeginningDateISOString =
    toISOStringWithoutMilliseconds(stockBeginningDate)
  const stockLocalBeginningDate = formatLocalTimeDateString(
    stockBeginningDateISOString,
    venueDepartmentCode,
    FORMAT_DD_MM_YYYY_HH_mm
  )

  const stockPrice: string = new Intl.NumberFormat("fr-FR", {
    style: "decimal",
    currency: "EUR",
  }).format(stock.price)

  return `${stockLocalBeginningDate}, ${stockPrice} €`
}

export const Stocks = ({
  stocks,
  venuePostalCode,
}: {
  stocks: StockType[];
  venuePostalCode: string;
}): JSX.Element => {
  return (
    <ul>
      {stocks.map((stock: StockType) => (
        <li key={stock.id}>
          {printStockInformation(stock, venuePostalCode)}
        </li>
      ))}
    </ul>
  )
}

export default Stocks
