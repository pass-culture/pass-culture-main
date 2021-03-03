import PropTypes from 'prop-types'
import React from 'react'

import Venue from 'components/pages/Home/Venues/Venue'

export const VenueList = ({ physicalVenues, selectedOffererId, virtualVenue }) => (
  <div className="h-venue-list">
    {virtualVenue && (
      <Venue
        id={virtualVenue.id}
        isVirtual
        name="Offres numériques"
        offererId={selectedOffererId}
      />
    )}

    {physicalVenues &&
      physicalVenues.map(venue => (
        <Venue
          id={venue.id}
          key={venue.id}
          name={venue.name}
          offererId={selectedOffererId}
          publicName={venue.publicName}
        />
      ))}
  </div>
)

VenueList.defaultProps = {
  physicalVenues: null,
  virtualVenue: null,
}

VenueList.propTypes = {
  physicalVenues: PropTypes.arrayOf(),
  selectedOffererId: PropTypes.string.isRequired,
  virtualVenue: PropTypes.shape(),
}
