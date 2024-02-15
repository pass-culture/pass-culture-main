import React from 'react'

import AccessibilitySummarySection from 'components/AccessibilitySummarySection'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'

interface CollectiveOfferAccessibilitySectionProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
}

const CollectiveOfferAccessibilitySection = ({
  offer,
}: CollectiveOfferAccessibilitySectionProps) => {
  return <AccessibilitySummarySection offer={offer} />
}

export default CollectiveOfferAccessibilitySection
