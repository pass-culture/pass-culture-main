import PropTypes from 'prop-types'
import React from 'react'

import { ALL_VENUES } from './_constants'

const FilterByVenue = ({ updateFilters, selectedVenue, venuesFormattedAndOrdered }) => {
  function handleVenueSelection(event) {
    const venueId = event.target.value
    updateFilters({ offerVenueId: venueId })
  }

  return (
    <div className="pf-venues">
      <label
        className="pf-offer-venue-label"
        htmlFor="offer-venue-input"
      >
        {'Lieu'}
      </label>
      <select
        id="offer-venue-input"
        onBlur={handleVenueSelection}
        onChange={handleVenueSelection}
        value={selectedVenue}
      >
        <option value={ALL_VENUES}>
          {'Tous les lieux'}
        </option>
        {venuesFormattedAndOrdered.map(venue => (
          <option
            key={venue.id}
            value={venue.id}
          >
            {venue.displayName}
          </option>
        ))}
      </select>
    </div>
  )
}

FilterByVenue.propTypes = {
  selectedVenue: PropTypes.string.isRequired,
  updateFilters: PropTypes.func.isRequired,
  venuesFormattedAndOrdered: PropTypes.arrayOf(
    PropTypes.shape({
      displayName: PropTypes.string.isRequired,
      id: PropTypes.string.isRequired,
    })
  ).isRequired,
}

export default FilterByVenue
