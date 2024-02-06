import React from 'react'

import { GetCollectiveOfferVenueResponseModel } from 'apiClient/v1'
import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

interface CollectiveOfferSummaryProps {
  venue: GetCollectiveOfferVenueResponseModel
}

const CollectiveOfferVenueSection = ({
  venue,
}: CollectiveOfferSummaryProps) => {
  return (
    <SummarySubSection title="Lieu de rattachement de votre offre">
      <SummaryRow title="Structure" description={venue.managingOfferer.name} />
      <SummaryRow title="Lieu" description={venue.publicName || venue.name} />
    </SummarySubSection>
  )
}

export default CollectiveOfferVenueSection
