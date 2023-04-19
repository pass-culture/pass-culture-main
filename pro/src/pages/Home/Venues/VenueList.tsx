import React from 'react'

import { GetOffererVenueResponseModel } from 'apiClient/v1'
import { getLastCollectiveDmsApplication } from 'core/Venue/adapters/getVenueAdapter/serializers'

import Venue from './Venue'

interface IVenueListProps {
  physicalVenues: GetOffererVenueResponseModel[]
  selectedOffererId: string
  virtualVenue: GetOffererVenueResponseModel | null
}

const VenueList = ({
  physicalVenues,
  selectedOffererId,
  virtualVenue,
}: IVenueListProps) => {
  return (
    <div className="h-venue-list">
      {virtualVenue && (
        <Venue
          id={virtualVenue.id}
          nonHumanizedId={virtualVenue.nonHumanizedId}
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
          id={venue.id}
          nonHumanizedId={venue.nonHumanizedId}
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
        />
      ))}
    </div>
  )
}

export default VenueList
