import React from 'react'

import { GetCollectiveOfferTemplateResponseModel } from 'apiClient/v1'
import { SummaryLayout } from 'new_components/SummaryLayout'

import CollectiveOfferVenueSection from './components/CollectiveOfferVenueSection'

interface ICollectiveOfferSummaryProps {
  offer: GetCollectiveOfferTemplateResponseModel
}

const CollectiveOfferSummary = ({ offer }: ICollectiveOfferSummaryProps) => {
  return (
    <SummaryLayout>
      <SummaryLayout.Content fullWidth>
        <SummaryLayout.Section
          title="Détails de l’offre"
          editLink={`/offre/T-${offer.id}/collectif/edition`}
        >
          <CollectiveOfferVenueSection venue={offer.venue} />
        </SummaryLayout.Section>
      </SummaryLayout.Content>
    </SummaryLayout>
  )
}

export default CollectiveOfferSummary
