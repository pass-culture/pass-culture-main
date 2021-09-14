import React, { useCallback } from "react"

import { Button } from "app/components/Layout/Button/Button"
import { preBookStock } from "repository/pcapi/pcapi"
import {
  FORMAT_DD_MM_YYYY_HH_mm,
  toISOStringWithoutMilliseconds,
} from "utils/date"
import { formatLocalTimeDateString } from "utils/timezone"
import { StockType } from "utils/types"

const displayStockInformation = (
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
  const preBookCurrentStock = useCallback(
    () => preBookStock(stock.id),
    [stock.id]
  )
  return (
    <li>
      {displayStockInformation(stock, venuePostalCode)}
      <Button
        onClick={preBookCurrentStock}
        text="Pré-réserver"
        type="button"
      />
    </li>
  )
}
