import React from 'react'

import Venue from 'components/pages/Home/Venues/VenueLegacy'

interface IVenueListProps {
  physicalVenues: {
    id: string
    name: string
    publicName?: string
    businessUnitId?: string
    hasReimbursementPoint: boolean
  }[]
  selectedOffererId: string
  virtualVenue: {
    id: string
    businessUnitId?: string
    hasReimbursementPoint: boolean
  } | null
}

export const VenueList = ({
  physicalVenues,
  selectedOffererId,
  virtualVenue,
}: IVenueListProps) => (
  <div className="h-venue-list">
    {virtualVenue && (
      <Venue
        hasBusinessUnit={!!virtualVenue.businessUnitId}
        id={virtualVenue.id}
        isVirtual
        name="Offres numériques"
        offererId={selectedOffererId}
        hasReimbursementPoint={virtualVenue.hasReimbursementPoint}
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
        hasReimbursementPoint={venue.hasReimbursementPoint}
      />
    ))}
  </div>
)
