import { GetCollectiveOfferTemplateResponseModel } from '@/apiClient//v1'
import {
  getRangeToFrenchText,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'

export type CollectiveOfferDateSectionProps = {
  offer: GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferDateSection = ({
  offer,
}: CollectiveOfferDateSectionProps) => {
  let description = 'Tout au long de l’année scolaire (l’offre est permanente)'

  if (offer.dates?.start && offer.dates.end) {
    const startDateWithoutTz = toDateStrippedOfTimezone(offer.dates.start)
    const endDateWithoutTz = toDateStrippedOfTimezone(offer.dates.end)

    description = getRangeToFrenchText(
      startDateWithoutTz,
      endDateWithoutTz,
      startDateWithoutTz.getHours() !== 0 ||
        startDateWithoutTz.getMinutes() !== 0
    )
  }

  return (
    <SummarySubSection title="Date et heure">
      <SummaryDescriptionList descriptions={[{ text: description }]} />
    </SummarySubSection>
  )
}
