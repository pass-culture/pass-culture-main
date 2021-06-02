import PropTypes from 'prop-types'
import React, { useEffect, useState, useCallback } from 'react'

import { formatAndOrderVenues, fetchAllVenuesByProUser } from 'repository/venuesService'
import { getToday } from 'utils/date'

import { ALL_VENUES, EMPTY_FILTER_VALUE } from './_constants'
import FilterByBookingPeriod from './FilterByBookingPeriod'
import FilterByEventDate from './FilterByEventDate.jsx'
import FilterByVenue from './FilterByVenue'

const PreFilters = ({ offerVenueId, applyPreFilters }) => {
  // eslint-disable-next-line no-unused-vars
  const [selectedFilters, setSelectedFilters] = useState({
    bookingBeginningDate: EMPTY_FILTER_VALUE,
    bookingEndingDate: getToday(),
    offerDate: EMPTY_FILTER_VALUE,
    offerVenueId: offerVenueId || ALL_VENUES,
  })
  const [venues, setVenues] = useState([])

  useEffect(() => {
    fetchAllVenuesByProUser().then(venues => setVenues(formatAndOrderVenues(venues)))
  }, [])

  const updateSelectedFilters = useCallback(updatedFilter => {
    setSelectedFilters(currentFilters => ({
      ...currentFilters,
      ...updatedFilter,
    }))
  }, [])

  const requestFilteredBookings = useCallback(
    event => {
      event.preventDefault()

      applyPreFilters(selectedFilters)
    },
    [applyPreFilters, selectedFilters]
  )

  return (
    <form onSubmit={requestFilteredBookings}>
      <div className="pre-filters">
        <FilterByVenue
          selectedVenue={selectedFilters.offerVenueId}
          updateFilters={updateSelectedFilters}
          venuesFormattedAndOrdered={venues}
        />
        <FilterByEventDate
          selectedOfferDate={selectedFilters.offerDate}
          updateFilters={updateSelectedFilters}
        />
        <FilterByBookingPeriod
          selectedBookingBeginningDate={selectedFilters.bookingBeginningDate}
          selectedBookingEndingDate={selectedFilters.bookingEndingDate}
          updateFilters={updateSelectedFilters}
        />
      </div>
      <div className="search-separator">
        <div className="separator" />
        <button
          className="primary-button"
          type="submit"
        >
          {'Afficher'}
        </button>
        <div className="separator" />
      </div>
    </form>
  )
}

PreFilters.defaultProps = {
  offerVenueId: null,
}

PreFilters.propTypes = {
  applyPreFilters: PropTypes.func.isRequired,
  offerVenueId: PropTypes.string,
}

export default PreFilters
