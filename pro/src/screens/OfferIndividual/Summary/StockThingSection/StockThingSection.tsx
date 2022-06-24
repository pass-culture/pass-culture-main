import { FORMAT_DD_MM_YYYY_HH_mm, toDateStrippedOfTimezone } from 'utils/date'

import React from 'react'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { format } from 'date-fns-tz'

export interface IStockThingSectionProps {
  quantity: number
  price: number
  bookingLimitDatetime: Date | null
}

const StockThingSection = ({
  quantity,
  price,
  bookingLimitDatetime,
}: IStockThingSectionProps): JSX.Element => {
  return (
    <SummaryLayout.Section title="Stocks et prix">
      <SummaryLayout.Row title="Prix" description={`${price} €`} />
      {bookingLimitDatetime !== null && (
        <SummaryLayout.Row
          title="Date limite de réservation"
          description={format(
            toDateStrippedOfTimezone(bookingLimitDatetime),
            FORMAT_DD_MM_YYYY_HH_mm
          )}
        />
      )}
      <SummaryLayout.Row
        title="Quantité"
        description={quantity || 'Illimité'}
      />
    </SummaryLayout.Section>
  )
}

export default StockThingSection
