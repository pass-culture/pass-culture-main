import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import * as pcapi from 'repository/pcapi/pcapi'
import { formatAndOrderVenues } from 'repository/venuesService'

import FilterByBookingPeriod from './FilterByBookingPeriod'
import FilterByEventDate from './FilterByEventDate.jsx'
import FilterByVenue from './FilterByVenue'

const PreFilters = ({ appliedPreFilters, applyPreFilters, isLoading }) => {
  const [selectedPreFilters, setSelectedPreFilters] = useState({ ...appliedPreFilters })
  const [venues, setVenues] = useState([])

  useEffect(() => {
    pcapi.getVenuesForOfferer().then(venues => setVenues(formatAndOrderVenues(venues)))
  }, [])

  useEffect(() => setSelectedPreFilters({ ...appliedPreFilters }), [appliedPreFilters])

  const updateSelectedFilters = useCallback(updatedFilter => {
    setSelectedPreFilters(currentFilters => ({
      ...currentFilters,
      ...updatedFilter,
    }))
  }, [])

  const requestFilteredBookings = useCallback(
    event => {
      event.preventDefault()

      applyPreFilters(selectedPreFilters)
    },
    [applyPreFilters, selectedPreFilters]
  )

  return (
    <form onSubmit={requestFilteredBookings}>
      <div className="pre-filters">
        <FilterByVenue
          selectedVenue={selectedPreFilters.offerVenueId}
          updateFilters={updateSelectedFilters}
          venuesFormattedAndOrdered={venues}
        />
        <FilterByEventDate
          selectedOfferDate={selectedPreFilters.offerEventDate}
          updateFilters={updateSelectedFilters}
        />
        <FilterByBookingPeriod
          selectedBookingBeginningDate={selectedPreFilters.bookingBeginningDate}
          selectedBookingEndingDate={selectedPreFilters.bookingEndingDate}
          updateFilters={updateSelectedFilters}
        />
      </div>
      <div className="search-separator">
        <div className="separator" />
        <button
          className="primary-button"
          disabled={isLoading}
          type="submit"
        >
          {'Afficher'}
        </button>
        <div className="separator" />
      </div>
    </form>
  )
}

PreFilters.propTypes = {
  appliedPreFilters: PropTypes.shape({
    bookingBeginningDate: PropTypes.instanceOf(Date).isRequired,
    bookingEndingDate: PropTypes.instanceOf(Date).isRequired,
    offerEventDate: PropTypes.oneOfType([PropTypes.instanceOf(Date), PropTypes.string]),
    offerVenueId: PropTypes.string.isRequired,
  }).isRequired,
  applyPreFilters: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
}

export default PreFilters
