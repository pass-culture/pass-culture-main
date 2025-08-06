import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient//v1'
import { Markdown } from '@/components/Markdown/Markdown'
import {
  Description,
  SummaryDescriptionList,
} from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'

import { DEFAULT_RECAP_VALUE } from './constants'
import { formatDuration } from './utils/formatDuration'

interface CollectiveOfferSummaryProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
}

export const CollectiveOfferTypeSection = ({
  offer,
}: CollectiveOfferSummaryProps) => {
  const offerTypeDescriptions: Description[] = []

  offerTypeDescriptions.push({
    title: 'Format',
    text: offer.formats.join(', ') || DEFAULT_RECAP_VALUE,
  })

  offerTypeDescriptions.push({
    title: 'Domaine artistique et culturel',
    text: offer.domains.map((domain) => domain.name).join(', '),
  })
  offerTypeDescriptions.push({
    title: 'Dispositif national',
    text: offer.nationalProgram?.name || DEFAULT_RECAP_VALUE,
  })

  return (
    <>
      <SummarySubSection title="Type d’offre">
        <SummaryDescriptionList descriptions={offerTypeDescriptions} />
      </SummarySubSection>

      <SummarySubSection title="Informations artistiques">
        <SummaryDescriptionList
          descriptions={[
            { title: 'Titre de l’offre', text: offer.name },
            {
              title: 'Description',
              text: !offer.description ? (
                DEFAULT_RECAP_VALUE
              ) : (
                <Markdown markdownText={offer.description} />
              ),
            },
            { title: 'Durée', text: formatDuration(offer.durationMinutes) },
          ]}
        />
      </SummarySubSection>
    </>
  )
}
