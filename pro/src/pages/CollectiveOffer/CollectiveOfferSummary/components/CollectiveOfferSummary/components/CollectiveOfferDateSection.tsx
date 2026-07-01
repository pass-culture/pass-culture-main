import type { GetCollectiveOfferTemplateResponseModel } from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import {
  getRangeToFrenchText,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

export type CollectiveOfferDateSectionProps = {
  offer: GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferDateSection = ({
  offer,
}: CollectiveOfferDateSectionProps) => {
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

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
    <SummarySubSection
      title="Date et heure"
      shouldShowDivider={!isNewCollectivePriceEnabled}
    >
      <SummaryDescriptionList descriptions={[{ text: description }]} />
    </SummarySubSection>
  )
}
