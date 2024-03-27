import React from 'react'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { AccessibilitySummarySection } from 'components/AccessibilitySummarySection/AccessibilitySummarySection'

interface CollectiveOfferAccessibilitySectionProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
}

const CollectiveOfferAccessibilitySection = ({
  offer,
}: CollectiveOfferAccessibilitySectionProps) => {
  return (
    <AccessibilitySummarySection
      accessibleItem={offer}
      accessibleWording="Votre offre est accessible aux publics en situation de handicap :"
    />
  )
}

export default CollectiveOfferAccessibilitySection
