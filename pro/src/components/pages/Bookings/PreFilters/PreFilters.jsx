/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import classNames from 'classnames'
import isEqual from 'lodash.isequal'
import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import * as pcapi from 'repository/pcapi/pcapi'
import { formatAndOrderVenues } from 'repository/venuesService'

import FilterByBookingPeriod from './FilterByBookingPeriod'
import FilterByEventDate from './FilterByEventDate.jsx'
import FilterByVenue from './FilterByVenue'

const PreFilters = ({
  appliedPreFilters,
  applyPreFilters,
  downloadBookingsCSV,
  hasResult,
  isTableLoading,
  isDownloadingCSV,
  wereBookingsRequested
}) => {
  const [selectedPreFilters, setSelectedPreFilters] = useState({ ...appliedPreFilters })
  const [venues, setVenues] = useState([])
  const [isLocalLoading, setIsLocalLoading] = useState(false)

  useEffect(() => {
    async function fetchVenues() {
      setIsLocalLoading(true)
      const venuesForOfferer = await pcapi.getVenuesForOfferer()
      setVenues(formatAndOrderVenues(venuesForOfferer))
      setIsLocalLoading(false)
    }
    fetchVenues()
  }, [setIsLocalLoading, setVenues])

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
  const downloadBookingsFilters = {
    page: 1,
    venueId: selectedPreFilters.offerVenueId,
    eventDate: selectedPreFilters.offerEventDate,
    bookingPeriodBeginningDate: selectedPreFilters.bookingBeginningDate,
    bookingPeriodEndingDate: selectedPreFilters.bookingEndingDate,
  }

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
        <div className="button-group">
          <span className="button-group-separator" />
          <div className="button-group-buttons">
            <button
              className="primary-button"
              disabled={isDownloadingCSV || isLocalLoading}
              onClick={() => downloadBookingsCSV(downloadBookingsFilters)}
              type="button"
            >
              Télécharger
            </button>
            <button
              className="secondary-button"
              disabled={isTableLoading || isLocalLoading}
              type="submit"
            >
              Afficher
            </button>
          </div>
        </div>
      </form>
      {isRefreshRequired && (
        <p
          className="pf-refresh-message"
          data-testid="refresh-required-message"
        >
          Vos filtres ont été modifiés. Veuillez cliquer sur « Afficher » pour actualiser votre
          recherche.
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
  downloadBookingsCSV: PropTypes.func.isRequired,
  hasResult: PropTypes.bool.isRequired,
  isDownloadingCSV: PropTypes.bool.isRequired,
  isTableLoading: PropTypes.bool.isRequired,
  wereBookingsRequested: PropTypes.bool.isRequired,
}

export default PreFilters
