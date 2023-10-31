import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { CollectiveOfferTemplate } from 'core/OfferEducational'

import { DEFAULT_RECAP_VALUE } from '../constants'

interface CollectiveOfferPriceSectionProps {
  offer: CollectiveOfferTemplate
}

export default function CollectiveOfferPriceSection({
  offer,
}: CollectiveOfferPriceSectionProps) {
  return (
    <SummaryLayout.SubSection title="Prix">
      <SummaryLayout.Row
        description={offer.educationalPriceDetail || DEFAULT_RECAP_VALUE}
      />
    </SummaryLayout.SubSection>
  )
}
