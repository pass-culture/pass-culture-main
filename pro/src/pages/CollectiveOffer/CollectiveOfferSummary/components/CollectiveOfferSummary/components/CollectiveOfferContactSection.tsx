import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { formatPhoneNumber } from '@/commons/utils/formatPhoneNumber'
import {
  type Description,
  SummaryDescriptionList,
} from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

interface CollectiveOfferContactSectionProps {
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferContactSection = ({
  offer,
}: CollectiveOfferContactSectionProps) => {
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  const isOfferTemplate = isCollectiveOfferTemplate(offer)

  const description: Description[] = [
    { title: 'Email', text: offer.contactEmail ?? '-' },
    {
      title: 'Téléphone',
      text: formatPhoneNumber(offer.contactPhone) || '-',
    },
  ]

  if (isOfferTemplate) {
    const formDescriptionText = offer.contactForm
      ? 'Le formulaire standard Pass Culture'
      : offer.contactUrl
    description.push({
      title: 'Formulaire de contact',
      text: formDescriptionText ?? '-',
    })
  }

  return (
    <SummarySubSection
      title="Contact"
      shouldShowDivider={!isNewCollectivePriceEnabled}
    >
      <SummaryDescriptionList descriptions={description} />
    </SummarySubSection>
  )
}
