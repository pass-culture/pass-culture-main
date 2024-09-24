import { useTranslation } from 'react-i18next'

import {
  GetCollectiveOfferTemplateResponseModel,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import { Markdown } from 'components/Markdown/Markdown'
import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

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
  const { t } = useTranslation('common')
  const offerTypeDescriptions: Description[] = []

  offerTypeDescriptions.push({
    title: 'Format',
    text: offer.formats?.join(', ') || DEFAULT_RECAP_VALUE,
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
      <SummarySubSection title={t('offer_type')}>
        <SummaryDescriptionList descriptions={offerTypeDescriptions} />
      </SummarySubSection>

      <SummarySubSection title="Informations artistiques">
        <SummaryDescriptionList
          descriptions={[
            { title: t('offer_title'), text: offer.name },
            {
              title: t('description'),
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
