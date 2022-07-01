import { FORMAT_DD_MM_YYYY_HH_mm, toDateStrippedOfTimezone } from 'utils/date'

import React from 'react'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { format } from 'date-fns-tz'

export interface IStockThingSectionProps {
  quantity?: number | null
  price: number
  bookingLimitDatetime: Date | null
}

interface IStockThingSummarySection extends IStockThingSectionProps {
  isCreation: boolean
  offerId: string
}

const StockThingSection = ({
  quantity,
  price,
  bookingLimitDatetime,
  isCreation,
  offerId,
}: IStockThingSummarySection): JSX.Element => {
  const editLink = isCreation
    ? `/offre/${offerId}/individuel/creation/stocks`
    : `/offre/${offerId}/individuel/stocks`
  return (
    <SummaryLayout.Section title="Stocks et prix" editLink={editLink}>
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
