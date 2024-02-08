import React from 'react'

import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { CollectiveOfferTemplate } from 'core/OfferEducational'

import { DEFAULT_RECAP_VALUE } from '../constants'

interface CollectiveOfferPriceSectionProps {
  offer: CollectiveOfferTemplate
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
