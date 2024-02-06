import { format } from 'date-fns-tz'
import React from 'react'

import { GetOfferStockResponseModel } from 'apiClient/v1'
import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'
import { formatPrice } from 'utils/formatPrice'

interface StockThingSectionProps {
  stock?: GetOfferStockResponseModel
  canBeDuo?: boolean
  isDuo: boolean
}

const StockThingSection = ({
  stock,
  canBeDuo,
  isDuo,
}: StockThingSectionProps) => {
  if (!stock) {
    return null
  }

  return (
    <>
      <SummaryRow title="Prix" description={formatPrice(stock.price)} />

      {stock.bookingLimitDatetime && (
        <SummaryRow
          title="Date limite de réservation"
          description={format(
            toDateStrippedOfTimezone(stock.bookingLimitDatetime),
            FORMAT_DD_MM_YYYY
          )}
        />
      )}

      <SummaryRow
        title="Quantité"
        description={
          stock.quantity !== null && stock.quantity !== undefined
            ? new Intl.NumberFormat('fr-FR').format(stock.quantity)
            : 'Illimité'
        }
      />

      {/* Some things offer can be duo like ESCAPE_GAME or CARTE_MUSEE */}
      {canBeDuo && (
        <SummaryRow
          title='Accepter les réservations "Duo"'
          description={isDuo ? 'Oui' : 'Non'}
        />
      )}
    </>
  )
}

export default StockThingSection
