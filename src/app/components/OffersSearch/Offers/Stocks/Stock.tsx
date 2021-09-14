import React from "react"

import { preBookStock } from "../../../../../repository/pcapi/pcapi"
import {
  FORMAT_DD_MM_YYYY_HH_mm,
  toISOStringWithoutMilliseconds,
} from "../../../../../utils/date"
import { formatLocalTimeDateString } from "../../../../../utils/timezone"
import { StockType } from "../../../../../utils/types"
import { Button } from "../../../Layout/Button/Button"

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

export const Stock = ({
  stock,
  venuePostalCode,
}: {
  stock: StockType;
  venuePostalCode: string;
}): JSX.Element => {
  return (
    <li>
      {printStockInformation(stock, venuePostalCode)}
      <Button
        onClick={() => preBookStock(stock.id)}
        text="Pré-réserver"
        type="button"
      />
    </li>
  )
}
