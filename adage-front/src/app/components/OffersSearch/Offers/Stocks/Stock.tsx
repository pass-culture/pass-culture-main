import React, { useCallback, useState } from "react"

import { Button } from "app/components/Layout/Button/Button"
import {
  Notification,
  NotificationComponent,
  NotificationType,
} from "app/components/Layout/Notification/Notification"
import { preBookStock } from "repository/pcapi/pcapi"
import {
  FORMAT_DD_MM_YYYY_HH_mm,
  toISOStringWithoutMilliseconds,
} from "utils/date"
import { formatLocalTimeDateString } from "utils/timezone"
import { StockType } from "utils/types"

const displayStockInformation = (
  stock: StockType,
  venuePostalCode: string
): string => {
  const departmentCode = extractDepartmentCode(venuePostalCode)
  const stockBeginningDate = new Date(stock.beginningDatetime)
  const stockBeginningDateISOString =
    toISOStringWithoutMilliseconds(stockBeginningDate)
  const stockLocalBeginningDate = formatLocalTimeDateString(
    stockBeginningDateISOString,
    departmentCode,
    FORMAT_DD_MM_YYYY_HH_mm
  )

  const stockPrice: string = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  }).format(stock.price / 100)

  return `${stockLocalBeginningDate}, ${stockPrice}`
}

const extractDepartmentCode = (venuePostalCode: string): string => {
  const departmentNumberBase: number = parseInt(venuePostalCode.slice(0, 2))
  if (departmentNumberBase > 95) {
    return venuePostalCode.slice(0, 3)
  } else {
    return venuePostalCode.slice(0, 2)
  }
}

export const Stock = ({
  canPrebookOffers,
  stock,
  venuePostalCode,
}: {
  canPrebookOffers: boolean;
  stock: StockType;
  venuePostalCode: string;
}): JSX.Element => {
  const [disableButton, setDisableButton] = useState(false)
  const [notification, setNotification] = useState<Notification | null>(null)
  const preBookCurrentStock = useCallback(() => {
    setDisableButton(true)
    return preBookStock(stock.id)
      .then(() =>
        setNotification(
          new Notification(
            NotificationType.success,
            "Votre préréservation a été effectuée avec succès."
          )
        )
      )
      .catch(() =>
        setNotification(
          new Notification(
            NotificationType.error,
            "Impossible de préréserver cette offre.\nVeuillez contacter le support"
          )
        )
      )
  }, [stock.id])
  return (
    <>
      <li>
        {displayStockInformation(stock, venuePostalCode)}

        {canPrebookOffers && (
          <Button
            disabled={disableButton}
            isSubmit={false}
            loadingMessage="Préreservation"
            onClick={preBookCurrentStock}
            text="Préréserver"
          />
        )}
      </li>
      {notification && <NotificationComponent notification={notification} />}
    </>
  )
}
