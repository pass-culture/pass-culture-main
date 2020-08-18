import { NavLink } from 'react-router-dom'
import PropTypes from 'prop-types'
import React from 'react'
import VenueItem from './VenueItem/VenueItem'
import { UNAVAILABLE_ERROR_PAGE } from '../../../../../utils/routes'

const Venues = ({ venues, offererId, isVenueCreationAvailable }) => {
  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  return (
    <div className="section op-content-section">
      <h2 className="main-list-title">
        {'Lieux'}
      </h2>
      <ul className="main-list venues-list">
        {venues.map(venue => (
          <VenueItem
            key={venue.id}
            venue={venue}
          />
        ))}
      </ul>
      <div className="has-text-centered">
        <NavLink
          className="tertiary-button"
          to={venueCreationUrl}
        >
          {'+ Ajouter un lieu'}
        </NavLink>
      </div>
    </div>
  )
}
Venues.propTypes = {
  offererId: PropTypes.string.isRequired,
  venues: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default Venues
