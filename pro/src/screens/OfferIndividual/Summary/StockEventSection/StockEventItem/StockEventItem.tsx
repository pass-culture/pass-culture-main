import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm } from 'utils/date'

import React from 'react'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { format } from 'date-fns-tz'

export interface IStockEventItemProps {
  className?: string
  beginningDatetime: string | Date | null
  price: number
  quantity?: number | null
  bookingLimitDatetime: string | Date | null
}

const StockEventItem = ({
  className,
  beginningDatetime,
  price,
  quantity,
  bookingLimitDatetime,
}: IStockEventItemProps): JSX.Element => {
  return (
    <div className={className}>
      {beginningDatetime && (
        <SummaryLayout.Row
          title="Date"
          description={format(beginningDatetime, FORMAT_DD_MM_YYYY)}
        />
      )}
      {beginningDatetime && (
        <SummaryLayout.Row
          title="Horaire"
          description={format(beginningDatetime, FORMAT_HH_mm)}
        />
      )}
      <SummaryLayout.Row title="Prix" description={`${price} €`} />
      {bookingLimitDatetime !== null && (
        <SummaryLayout.Row
          title="Date limite de réservation"
          description={format(bookingLimitDatetime, FORMAT_DD_MM_YYYY)}
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
