import { format } from 'date-fns-tz'
import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { IndividualOfferStock } from 'core/Offers/types'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'
import { formatPrice } from 'utils/formatPrice'

interface StockThingSectionProps {
  stock?: IndividualOfferStock
}

const StockThingSection = ({ stock }: StockThingSectionProps) => {
  if (!stock) {
    return null
  }

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
    </>
  )
}

export default StockThingSection
