import React from 'react'

import { SummaryLayout } from 'new_components/SummaryLayout'
import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm } from 'utils/date'
import { formatLocalTimeDateString } from 'utils/timezone'

export interface IStockEventItemProps {
  className?: string
  beginningDatetime: string | Date | null
  price: number
  quantity?: number | null
  bookingLimitDatetime: string | Date | null
  activationCodesExpirationDatetime?: Date | null
  departementCode: string
}

const StockEventItem = ({
  className,
  beginningDatetime,
  price,
  quantity,
  bookingLimitDatetime,
  departementCode,
}: IStockEventItemProps): JSX.Element => {
  return (
    <div className={className}>
      {beginningDatetime && (
        <SummaryLayout.Row
          title="Date"
          description={formatLocalTimeDateString(
            beginningDatetime,
            departementCode,
            FORMAT_DD_MM_YYYY
          )}
        />
      )}
      {beginningDatetime && (
        <SummaryLayout.Row
          title="Horaire"
          description={formatLocalTimeDateString(
            beginningDatetime,
            departementCode,
            FORMAT_HH_mm
          )}
        />
      )}
      <SummaryLayout.Row title="Prix" description={`${price} €`} />
      {bookingLimitDatetime !== null && (
        <SummaryLayout.Row
          title="Date limite de réservation"
          description={formatLocalTimeDateString(
            bookingLimitDatetime,
            departementCode,
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
