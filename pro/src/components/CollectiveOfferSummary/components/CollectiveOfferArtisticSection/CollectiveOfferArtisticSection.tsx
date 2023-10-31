import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'

import { DEFAULT_RECAP_VALUE } from '../constants'
import { formatDuration } from '../utils/formatDuration'

interface CollectiveOfferArtisticSectionProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
}

export default function CollectiveOfferArtisticSection({
  offer,
}: CollectiveOfferArtisticSectionProps) {
  return (
    <SummaryLayout.SubSection title="Informations artistiques">
      <SummaryLayout.Row title="Titre de l’offre" description={offer.name} />
      <SummaryLayout.Row
        title="Description"
        description={offer.description || DEFAULT_RECAP_VALUE}
      />
      <SummaryLayout.Row
        title="Durée"
        description={formatDuration(offer.durationMinutes)}
      />
    </SummaryLayout.SubSection>
  )
}
