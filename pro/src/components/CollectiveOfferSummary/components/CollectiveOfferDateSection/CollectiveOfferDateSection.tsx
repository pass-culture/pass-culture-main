import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { CollectiveOfferTemplate } from 'core/OfferEducational'
import { getRangeToFrenchText, toDateStrippedOfTimezone } from 'utils/date'

export type CollectiveOfferDateSectionProps = {
  offer: CollectiveOfferTemplate
}

export default function CollectiveOfferDateSection({
  offer,
}: CollectiveOfferDateSectionProps) {
  if (!offer.dates?.start || !offer.dates?.end) {
    return null
  }

  const startDateWithoutTz = toDateStrippedOfTimezone(offer.dates.start)
  const endDateWithoutTz = toDateStrippedOfTimezone(offer.dates.end)

  const datesFormatted = getRangeToFrenchText(
    startDateWithoutTz,
    endDateWithoutTz
  )

  return (
    <SummaryLayout.SubSection title="Date et heure">
      <SummaryLayout.Row description={datesFormatted} />
    </SummaryLayout.SubSection>
  )
}
