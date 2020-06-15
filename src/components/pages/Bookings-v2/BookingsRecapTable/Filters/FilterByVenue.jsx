import React from 'react'
import PropTypes from 'prop-types'
import { ALL_VENUES } from './Filters'

const FilterByVenue = ({ isDisabled, updateFilters, selectedVenue, venuesFormattedAndOrdered }) => {
  function handleVenueSelection(event) {
    const venueId = event.target.value
    const updatedFilter = { offerVenue: venueId }
    const updatedSelectedContent = { selectedVenue: venueId }
    updateFilters(updatedFilter, updatedSelectedContent)
  }

  return (
    <div className="fw-venues">
      <label
        className="fw-offer-venue-label"
        htmlFor="offer-venue-input"
      >
        {'Lieu'}
      </label>
      <select
        disabled={isDisabled}
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
  isDisabled: PropTypes.bool.isRequired,
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
