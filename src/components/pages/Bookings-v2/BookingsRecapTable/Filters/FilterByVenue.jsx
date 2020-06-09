import React from 'react'
import { ALL_VENUES } from '../utils/filterBookingsRecap'
import PropTypes from 'prop-types'

const FilterByVenue = ({
  onHandleVenueSelection,
  selectedVenue,
  venueSelect,
  venuesFormattedAndOrdered,
}) => {
  return (
    <div className="fw-venues">
      <label
        className="fw-offer-venue-label"
        htmlFor="offer-venue-input"
      >
        {'Lieu'}
      </label>
      <select
        id="offer-venue-input"
        onBlur={onHandleVenueSelection}
        onChange={onHandleVenueSelection}
        ref={venueSelect}
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
  onHandleVenueSelection: PropTypes.func.isRequired,
  selectedVenue: PropTypes.string.isRequired,
  venueSelect: PropTypes.string.isRequired,
  venuesFormattedAndOrdered: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      displayName: PropTypes.string.isRequired,
    })
  ).isRequired,
}

export default FilterByVenue
