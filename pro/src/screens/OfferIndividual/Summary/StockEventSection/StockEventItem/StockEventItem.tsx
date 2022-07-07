import {
  FORMAT_DD_MM_YYYY,
  FORMAT_HH_mm,
  toDateStrippedOfTimezone,
} from 'utils/date'

import React from 'react'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { format } from 'date-fns-tz'

export interface IStockEventItemProps {
  className?: string
  beginningDateTime: string | null
  price: number
  quantity?: number | null
  bookingLimitDatetime: string | null
}

const StockEventItem = ({
  className,
  beginningDateTime,
  price,
  quantity,
  bookingLimitDatetime,
}: IStockEventItemProps): JSX.Element => {
  const eventLocalDateTime = toDateStrippedOfTimezone(beginningDateTime)
  return (
    <div className={className}>
      {beginningDateTime && (
        <SummaryLayout.Row
          title="Date"
          description={format(eventLocalDateTime, FORMAT_DD_MM_YYYY)}
        />
      )}
      {beginningDateTime && (
        <SummaryLayout.Row
          title="Horaire"
          description={format(eventLocalDateTime, FORMAT_HH_mm)}
        />
      )}
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
        description={quantity || 'Illimité'}
      />
    </div>
  )
}

export default StockEventItem
