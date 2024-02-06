import React from 'react'

import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
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
      <SummaryRow
        description={offer.educationalPriceDetail || DEFAULT_RECAP_VALUE}
      />
    </SummarySubSection>
  )
}
