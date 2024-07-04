import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { isCollectiveOfferTemplate } from 'core/OfferEducational/types'

interface CollectiveOfferContactSectionProps {
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferContactSection = ({
  offer,
}: CollectiveOfferContactSectionProps) => {
  const isOfferTemplate = isCollectiveOfferTemplate(offer)

  const description: Description[] = [
    { title: 'Email', text: offer.contactEmail ?? '-' },
    { title: 'Téléphone', text: offer.contactPhone ?? '-' },
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
    <SummarySubSection title="Contact">
      <SummaryDescriptionList descriptions={description} />
    </SummarySubSection>
  )
}
