import React from 'react'

import { GetCollectiveOfferTemplateResponseModel } from 'apiClient/v1'
import { EducationalCategories } from 'core/OfferEducational'
import { SummaryLayout } from 'new_components/SummaryLayout'

import CollectiveOfferAccessibilitySection from './components/CollectiveOfferAccessibilitySection'
import CollectiveOfferParticipantSection from './components/CollectiveOfferParticipantSection'
import CollectiveOfferPracticalInformation from './components/CollectiveOfferPracticalInformation'
import CollectiveOfferTypeSection from './components/CollectiveOfferTypeSection'
import CollectiveOfferVenueSection from './components/CollectiveOfferVenueSection'

interface ICollectiveOfferSummaryProps {
  offer: GetCollectiveOfferTemplateResponseModel
  categories: EducationalCategories
}

const CollectiveOfferSummary = ({
  offer,
  categories,
}: ICollectiveOfferSummaryProps) => {
  return (
    <SummaryLayout>
      <SummaryLayout.Content fullWidth>
        <SummaryLayout.Section
          title="Détails de l’offre"
          editLink={`/offre/T-${offer.id}/collectif/edition`}
        >
          <CollectiveOfferVenueSection venue={offer.venue} />
          <CollectiveOfferTypeSection offer={offer} categories={categories} />
          <CollectiveOfferPracticalInformation offer={offer} />
          <CollectiveOfferParticipantSection students={offer.students} />
          <CollectiveOfferAccessibilitySection offer={offer} />
        </SummaryLayout.Section>
      </SummaryLayout.Content>
    </SummaryLayout>
  )
}

export default CollectiveOfferSummary
