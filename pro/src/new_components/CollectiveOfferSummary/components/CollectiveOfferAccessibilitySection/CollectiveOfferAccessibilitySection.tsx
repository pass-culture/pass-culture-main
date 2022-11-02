import React from 'react'

import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import { AccessibilitySummarySection } from 'new_components/AccessibilitySummarySection'

interface ICollectiveOfferParticipantSectionProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
}

const CollectiveOfferParticipantSection = ({
  offer,
}: ICollectiveOfferParticipantSectionProps) => {
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
