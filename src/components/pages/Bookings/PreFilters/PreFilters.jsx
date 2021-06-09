import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import * as pcapi from 'repository/pcapi/pcapi'
import { formatAndOrderVenues } from 'repository/venuesService'

import { DEFAULT_PRE_FILTERS } from './_constants'
import FilterByBookingPeriod from './FilterByBookingPeriod'
import FilterByEventDate from './FilterByEventDate.jsx'
import FilterByVenue from './FilterByVenue'

const PreFilters = ({ applyPreFilters, isLoading, offerVenueId }) => {
  const [selectedPreFilters, setSelectedPreFilters] = useState({
    bookingBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
    bookingEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
    offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
    offerVenueId: offerVenueId,
  })
  const [venues, setVenues] = useState([])

  useEffect(() => {
    pcapi.getVenuesForOfferer().then(venues => setVenues(formatAndOrderVenues(venues)))
  }, [])

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

PreFilters.defaultProps = {
  offerVenueId: DEFAULT_PRE_FILTERS.offerVenueId,
}

PreFilters.propTypes = {
  applyPreFilters: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  offerVenueId: PropTypes.string,
}

export default PreFilters
