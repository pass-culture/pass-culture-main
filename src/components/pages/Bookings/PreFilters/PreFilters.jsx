import classNames from 'classnames'
import isEqual from 'lodash.isequal'
import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import * as pcapi from 'repository/pcapi/pcapi'
import { formatAndOrderVenues } from 'repository/venuesService'

import FilterByBookingPeriod from './FilterByBookingPeriod'
import FilterByEventDate from './FilterByEventDate.jsx'
import FilterByVenue from './FilterByVenue'

const PreFilters = ({ appliedPreFilters, applyPreFilters, hasResult, isLoading, wereBookingsRequested }) => {
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

  const isRefreshRequired = !isEqual(selectedPreFilters, appliedPreFilters) && wereBookingsRequested

  return (
    <>
      <form
        className={classNames({
          'has-result': hasResult,
          'refresh-required': isRefreshRequired,
        })}
        onSubmit={requestFilteredBookings}
      >
        <div className="pre-filters">
          <FilterByVenue
            selectedVenueId={selectedPreFilters.offerVenueId}
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
      {isRefreshRequired && (
        <p className="pf-refresh-message">
          {
            'Vos filtres ont été modifiés. Veuillez cliquer sur « Afficher » pour actualiser votre recherche.'
          }
        </p>
      )}
    </>
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
  hasResult: PropTypes.bool.isRequired,
  isLoading: PropTypes.bool.isRequired,
  wereBookingsRequested: PropTypes.bool.isRequired,
}

export default PreFilters
