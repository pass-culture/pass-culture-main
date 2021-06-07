import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import * as pcapi from 'repository/pcapi/pcapi'
import { formatAndOrderVenues } from 'repository/venuesService'

import { DEFAULT_PRE_FILTERS } from './_constants'
import FilterByBookingPeriod from './FilterByBookingPeriod'
import FilterByEventDate from './FilterByEventDate.jsx'
import FilterByVenue from './FilterByVenue'

const PreFilters = ({ offerVenueId, applyPreFilters }) => {
  const [selectedFilters, setSelectedFilters] = useState({
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
          selectedOfferDate={selectedFilters.offerEventDate}
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
  offerVenueId: DEFAULT_PRE_FILTERS.offerVenueId,
}

PreFilters.propTypes = {
  applyPreFilters: PropTypes.func.isRequired,
  offerVenueId: PropTypes.string,
}

export default PreFilters
