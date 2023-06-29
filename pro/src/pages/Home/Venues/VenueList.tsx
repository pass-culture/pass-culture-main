import React from 'react'

import { GetOffererVenueResponseModel } from 'apiClient/v1'
import { getLastCollectiveDmsApplication } from 'utils/getLastCollectiveDmsApplication'

import Venue from './Venue'

interface VenueListProps {
  physicalVenues: GetOffererVenueResponseModel[]
  selectedOffererId: number
  virtualVenue: GetOffererVenueResponseModel | null
}

const VenueList = ({
  physicalVenues,
  selectedOffererId,
  virtualVenue,
}: VenueListProps) => {
  return (
    <div className="h-venue-list">
      {virtualVenue && (
        <Venue
          venueId={virtualVenue.nonHumanizedId}
          isVirtual
          name="Offres numériques"
          offererId={selectedOffererId}
          hasMissingReimbursementPoint={
            virtualVenue.hasMissingReimbursementPoint
          }
          hasCreatedOffer={virtualVenue.hasCreatedOffer}
          dmsInformations={getLastCollectiveDmsApplication(
            virtualVenue.collectiveDmsApplications
          )}
          hasAdageId={virtualVenue.hasAdageId}
          adageInscriptionDate={virtualVenue.adageInscriptionDate}
        />
      )}

      {physicalVenues?.map(venue => (
        <Venue
          venueId={venue.nonHumanizedId}
          key={selectedOffererId + '-' + venue.nonHumanizedId}
          name={venue.name}
          offererId={selectedOffererId}
          publicName={venue.publicName}
          hasMissingReimbursementPoint={venue.hasMissingReimbursementPoint}
          hasCreatedOffer={venue.hasCreatedOffer}
          dmsInformations={getLastCollectiveDmsApplication(
            venue.collectiveDmsApplications
          )}
          hasAdageId={venue.hasAdageId}
          adageInscriptionDate={venue.adageInscriptionDate}
        />
      ))}
    </div>
  )
}

export default VenueList
