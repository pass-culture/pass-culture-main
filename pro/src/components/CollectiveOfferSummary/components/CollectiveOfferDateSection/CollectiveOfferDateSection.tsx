import React from 'react'

import { GetCollectiveOfferTemplateResponseModel } from 'apiClient/v1'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { getRangeToFrenchText, toDateStrippedOfTimezone } from 'utils/date'

export type CollectiveOfferDateSectionProps = {
  offer: GetCollectiveOfferTemplateResponseModel
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
    <SummarySubSection title="Date et heure">
      <SummaryDescriptionList descriptions={[{ text: description }]} />
    </SummarySubSection>
  )
}
