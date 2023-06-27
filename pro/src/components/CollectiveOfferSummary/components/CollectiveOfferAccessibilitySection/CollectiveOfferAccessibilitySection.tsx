import React from 'react'

import AccessibilitySummarySection from 'components/AccessibilitySummarySection'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'

interface CollectiveOfferParticipantSectionProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
}

const CollectiveOfferParticipantSection = ({
  offer,
}: CollectiveOfferParticipantSectionProps) => {
  const noDisabilityCompliance =
    !offer.audioDisabilityCompliant &&
    !offer.motorDisabilityCompliant &&
    !offer.mentalDisabilityCompliant &&
    !offer.visualDisabilityCompliant

  return (
    <AccessibilitySummarySection
      noDisabilityCompliance={noDisabilityCompliance}
      audioDisabilityCompliant={Boolean(offer.audioDisabilityCompliant)}
      motorDisabilityCompliant={Boolean(offer.motorDisabilityCompliant)}
      mentalDisabilityCompliant={Boolean(offer.mentalDisabilityCompliant)}
      visualDisabilityCompliant={Boolean(offer.visualDisabilityCompliant)}
    />
  )
}

export default CollectiveOfferParticipantSection
