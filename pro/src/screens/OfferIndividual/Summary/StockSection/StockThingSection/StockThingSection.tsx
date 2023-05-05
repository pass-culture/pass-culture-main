import { format } from 'date-fns-tz'
import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { IOfferIndividual } from 'core/Offers/types'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'
import { formatPrice } from 'utils/formatPrice'

interface IStockThingSectionProps {
  offer: IOfferIndividual
  canBeDuo?: boolean
}

const StockThingSection = ({ offer, canBeDuo }: IStockThingSectionProps) => {
  if (offer.isEvent || offer.stocks.length === 0) {
    return null
  }

  const stock = offer.stocks[0]

  return (
    <>
      <SummaryLayout.Row title="Prix" description={formatPrice(stock.price)} />

      {stock.bookingLimitDatetime !== null && (
        <SummaryLayout.Row
          title="Date limite de réservation"
          description={format(
            toDateStrippedOfTimezone(stock.bookingLimitDatetime),
            FORMAT_DD_MM_YYYY
          )}
        />
      )}

      <SummaryLayout.Row
        title="Quantité"
        description={stock.quantity ?? 'Illimité'}
      />

      {canBeDuo && (
        <SummaryLayout.Row
          title='Accepter les réservations "Duo"'
          description={offer.isDuo ? 'Oui' : 'Non'}
        />
      )}
    </>
  )
}

export default StockThingSection
