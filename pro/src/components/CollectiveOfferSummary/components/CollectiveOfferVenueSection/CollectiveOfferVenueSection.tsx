import React from 'react'

import { GetCollectiveOfferVenueResponseModel } from 'apiClient/v1'
import { SummaryLayout } from 'components/SummaryLayout'

interface CollectiveOfferSummaryProps {
  venue: GetCollectiveOfferVenueResponseModel
}

const CollectiveOfferVenueSection = ({
  venue,
}: CollectiveOfferSummaryProps) => {
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
