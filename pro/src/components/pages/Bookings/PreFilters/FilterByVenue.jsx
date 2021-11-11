/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React from 'react'

import Select from 'components/layout/inputs/Select'

import { ALL_VENUES_OPTION } from './_constants'

const FilterByVenue = ({ updateFilters, selectedVenueId, venuesFormattedAndOrdered }) => {
  function handleVenueSelection(event) {
    const venueId = event.target.value
    updateFilters({ offerVenueId: venueId })
  }

  const venueOptions = venuesFormattedAndOrdered.map(venue => ({
    id: venue.id,
    displayName: venue.displayName
  }))

  return (
    <Select
      defaultOption={ALL_VENUES_OPTION}
      handleSelection={handleVenueSelection}
      label="Lieu"
      name="lieu"
      options={venueOptions}
      selectedValue={selectedVenueId}
    />
  )
}

FilterByVenue.propTypes = {
  selectedVenueId: PropTypes.string.isRequired,
  updateFilters: PropTypes.func.isRequired,
  venuesFormattedAndOrdered: PropTypes.arrayOf(
    PropTypes.shape({
      displayName: PropTypes.string.isRequired,
      id: PropTypes.string.isRequired,
    })
  ).isRequired,
}

export default FilterByVenue
