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
  let description = 'Tout au long de l’année scolaire (l’offre est permanente)'

  if (offer.dates?.start && offer.dates?.end) {
    const startDateWithoutTz = toDateStrippedOfTimezone(offer.dates.start)
    const endDateWithoutTz = toDateStrippedOfTimezone(offer.dates.end)

    description = getRangeToFrenchText(startDateWithoutTz, endDateWithoutTz)
  }

  return (
    <SummaryLayout.SubSection title="Date et heure">
      <SummaryLayout.Row description={description} />
    </SummaryLayout.SubSection>
  )
}
