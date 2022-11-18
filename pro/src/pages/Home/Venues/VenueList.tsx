import React from 'react'

import Venue from './Venue'

interface IVenueListProps {
  physicalVenues: {
    id: string
    name: string
    publicName?: string
    businessUnitId?: string
    hasMissingReimbursementPoint: boolean
  }[]
  selectedOffererId: string
  virtualVenue: {
    id: string
    businessUnitId?: string
    hasMissingReimbursementPoint: boolean
  } | null
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
          hasBusinessUnit={!!virtualVenue.businessUnitId}
          id={virtualVenue.id}
          isVirtual
          name="Offres numériques"
          offererId={selectedOffererId}
          hasMissingReimbursementPoint={
            virtualVenue.hasMissingReimbursementPoint
          }
        />
      )}

      {physicalVenues?.map(venue => (
        <Venue
          hasBusinessUnit={!!venue.businessUnitId}
          id={venue.id}
          key={venue.id}
          name={venue.name}
          offererId={selectedOffererId}
          publicName={venue.publicName}
          hasMissingReimbursementPoint={venue.hasMissingReimbursementPoint}
        />
      ))}
    </div>
  )
}

export default VenueList
