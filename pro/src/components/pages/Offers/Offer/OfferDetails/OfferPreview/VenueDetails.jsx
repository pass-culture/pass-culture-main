import PropTypes from 'prop-types'
import React from 'react'

export const VenueDetails = ({ physicalVenue }) => {
  const venueName = physicalVenue.publicName || physicalVenue.name
  const venueDetails = [
    venueName,
    physicalVenue.address,
    physicalVenue.postalCode,
    physicalVenue.city,
  ]

  return (
    <div className="op-section">
      <div className="op-section-title">Où ?</div>
      <div className="op-section-secondary-title">Adresse</div>
      <address className="op-section-text op-address">
        {venueDetails.filter(venueDetail => Boolean(venueDetail)).join(' - ')}
      </address>
      <div className="op-section-secondary-title">Distance</div>
      <div className="op-section-text">- - km</div>
    </div>
  )
}

VenueDetails.propTypes = {
  physicalVenue: PropTypes.shape({
    name: PropTypes.string,
    publicName: PropTypes.string,
    address: PropTypes.string,
    postalCode: PropTypes.string,
    city: PropTypes.string,
  }).isRequired,
}
