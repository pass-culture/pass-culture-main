import { format } from 'date-fns-tz'
import React from 'react'

import { GetOfferStockResponseModel } from 'apiClient/v1'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'
import { formatPrice } from 'utils/formatPrice'

interface StockThingSectionProps {
  stock?: GetOfferStockResponseModel
  canBeDuo?: boolean
  isDuo: boolean
}

export const StockThingSection = ({
  stock,
  canBeDuo,
  isDuo,
}: StockThingSectionProps) => {
  if (!stock) {
    return null
  }

  const descriptions = []
  descriptions.push({ title: 'Prix', text: formatPrice(stock.price) })
  if (stock.bookingLimitDatetime) {
    descriptions.push({
      title: 'Date limite de réservation',
      text: format(
        toDateStrippedOfTimezone(stock.bookingLimitDatetime),
        FORMAT_DD_MM_YYYY
      ),
    })
  }
  descriptions.push({
    title: 'Quantité',
    text:
      stock.quantity !== null && stock.quantity !== undefined
        ? new Intl.NumberFormat('fr-FR').format(stock.quantity)
        : 'Illimité',
  })
  {
    /* Some things offer can be duo like ESCAPE_GAME or CARTE_MUSEE */
  }
  if (canBeDuo) {
    descriptions.push({
      title: 'Accepter les réservations "Duo"',
      text: isDuo ? 'Oui' : 'Non',
    })
  }

  return <SummaryDescriptionList descriptions={descriptions} />
}
