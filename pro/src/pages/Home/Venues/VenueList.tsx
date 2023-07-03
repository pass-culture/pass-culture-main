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
          venueId={virtualVenue.id}
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
          hasPendingBankInformationApplication={
            virtualVenue.hasPendingBankInformationApplication
          }
        />
      )}

      {physicalVenues?.map(venue => (
        <Venue
          venueId={venue.id}
          key={selectedOffererId + '-' + venue.id}
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
          hasPendingBankInformationApplication={
            venue.hasPendingBankInformationApplication
          }
        />
      ))}
    </div>
  )
}

export default VenueList
