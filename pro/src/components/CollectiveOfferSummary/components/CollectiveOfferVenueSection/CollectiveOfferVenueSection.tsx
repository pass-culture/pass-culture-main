import React from 'react'

import { GetCollectiveOfferVenueResponseModel } from 'apiClient/v1'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

interface CollectiveOfferSummaryProps {
  venue: GetCollectiveOfferVenueResponseModel
}

const CollectiveOfferVenueSection = ({
  venue,
}: CollectiveOfferSummaryProps) => {
  return (
    <SummarySubSection title="Lieu de rattachement de votre offre">
      <SummaryDescriptionList
        descriptions={[
          { title: 'Structure', text: venue.managingOfferer.name },
          { title: 'Lieu', text: venue.publicName || venue.name },
        ]}
      />
    </SummarySubSection>
  )
}

export default CollectiveOfferVenueSection
