import React from 'react'

import { GetCollectiveOfferVenueResponseModel } from 'apiClient/v1'
import { SummaryLayout } from 'new_components/SummaryLayout'

interface ICollectiveOfferSummaryProps {
  venue: GetCollectiveOfferVenueResponseModel
}

const CollectiveOfferVenueSection = ({
  venue,
}: ICollectiveOfferSummaryProps) => {
  return (
    <SummaryLayout.SubSection title="Lieu de rattachement de votre offre">
      <SummaryLayout.Row
        title="Structure"
        description={venue.managingOfferer.name}
      />
      <SummaryLayout.Row
        title="Lieu"
        description={venue.publicName ?? venue.name}
      />
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferVenueSection
