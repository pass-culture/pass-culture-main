import { format } from 'date-fns-tz'
import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'

export interface IStockThingSectionProps {
  quantity?: number | null
  price: number
  bookingLimitDatetime: string | null
}

const StockThingSection = ({
  quantity,
  price,
  bookingLimitDatetime,
}: IStockThingSectionProps): JSX.Element => {
  return (
    <>
      <SummaryLayout.Row title="Prix" description={`${price} €`} />
      {bookingLimitDatetime !== null && (
        <SummaryLayout.Row
          title="Date limite de réservation"
          description={format(
            toDateStrippedOfTimezone(bookingLimitDatetime),
            FORMAT_DD_MM_YYYY
          )}
        />
      )}
      <SummaryLayout.Row
        title="Quantité"
        description={quantity ?? 'Illimité'}
      />
    </>
  )
}

export default StockThingSection
