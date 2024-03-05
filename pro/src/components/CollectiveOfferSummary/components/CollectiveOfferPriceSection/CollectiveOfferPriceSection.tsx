import React from 'react'

import { GetCollectiveOfferTemplateResponseModel } from 'apiClient/v1'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

import { DEFAULT_RECAP_VALUE } from '../constants'

interface CollectiveOfferPriceSectionProps {
  offer: GetCollectiveOfferTemplateResponseModel
}

export default function CollectiveOfferPriceSection({
  offer,
}: CollectiveOfferPriceSectionProps) {
  return (
    <SummarySubSection title="Prix">
      <SummaryDescriptionList
        descriptions={[
          { text: offer.educationalPriceDetail || DEFAULT_RECAP_VALUE },
        ]}
      />
    </SummarySubSection>
  )
}
