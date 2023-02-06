import { format } from 'date-fns-tz'
import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { IOfferIndividual } from 'core/Offers/types'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'

interface IStockThingSectionProps {
  offer: IOfferIndividual
}

const StockThingSection = ({ offer }: IStockThingSectionProps) => {
  if (offer.isEvent || offer.stocks.length === 0) {
    return null
  }

  const stock = offer.stocks[0]

  return (
    <>
      <SummaryLayout.Row
        title="Prix"
        description={`${stock.price.toString().replace('.', ',')} €`}
      />
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
    </>
  )
}

export default StockThingSection
