import React from 'react'

import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import { SummaryLayout } from 'new_components/SummaryLayout'

import { formatOfferEventAddress } from '../utils/formatOfferEventAddress'

interface ICollectiveOfferPracticalInformationSectionProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
}

const CollectiveOfferPracticalInformationSection = ({
  offer,
}: ICollectiveOfferPracticalInformationSectionProps) => {
  return (
    <SummaryLayout.SubSection title="Informations pratiques">
      <SummaryLayout.Row
        title="Adresse où se déroulera l’évènement"
        description={formatOfferEventAddress(offer.offerVenue, offer.venue)}
      />
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferPracticalInformationSection
