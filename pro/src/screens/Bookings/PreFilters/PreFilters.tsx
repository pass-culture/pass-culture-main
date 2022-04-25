import classNames from 'classnames'
import isEqual from 'lodash.isequal'
import React, { useCallback, useEffect, useState } from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'
import { TPreFilters } from 'core/Bookings'
import { GetBookingsCSVFileAdapter } from 'core/Bookings'
import FilterByOfferType from 'new_components/FilterByOfferType'

import FilterByBookingPeriod from './FilterByBookingPeriod'
import FilterByBookingStatusPeriod from './FilterByBookingStatusPeriod'
import FilterByEventDate from './FilterByEventDate'
import FilterByVenue from './FilterByVenue'

export interface IPreFiltersProps {
  appliedPreFilters: TPreFilters
  applyPreFilters: (filters: TPreFilters) => void
  hasResult: boolean
  isBookingFiltersActive: boolean
  isFiltersDisabled: boolean
  isTableLoading: boolean
  wereBookingsRequested: boolean
  isLocalLoading: boolean
  venues: { id: string; displayName: string }[]
  getBookingsCSVFileAdapter: GetBookingsCSVFileAdapter
}

const PreFilters = ({
  appliedPreFilters,
  applyPreFilters,
  hasResult,
  isBookingFiltersActive,
  isFiltersDisabled,
  isTableLoading,
  wereBookingsRequested,
  isLocalLoading,
  venues,
  getBookingsCSVFileAdapter,
}: IPreFiltersProps): JSX.Element => {
  const notify = useNotification()
  const separateIndividualAndCollectiveOffers = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )
  const [selectedPreFilters, setSelectedPreFilters] = useState({
    ...appliedPreFilters,
  })
  const [isDownloadingCSV, setIsDownloadingCSV] = useState(false)

  useEffect(
    () => setSelectedPreFilters({ ...appliedPreFilters }),
    [appliedPreFilters]
  )

  const updateSelectedFilters = useCallback(
    updatedFilter => {
      if (updatedFilter.offerEventDate) {
        updatedFilter.bookingBeginningDate = null
        updatedFilter.bookingEndingDate = null
        if (updatedFilter.offerEventDate === appliedPreFilters.offerEventDate) {
          updatedFilter.bookingBeginningDate =
            appliedPreFilters.bookingBeginningDate
          updatedFilter.bookingEndingDate = appliedPreFilters.bookingEndingDate
        }
      }
      setSelectedPreFilters(currentFilters => ({
        ...currentFilters,
        ...updatedFilter,
      }))
    },
    [appliedPreFilters]
  )

  const requestFilteredBookings = useCallback(
    event => {
      event.preventDefault()
      applyPreFilters(selectedPreFilters)
    },
    [applyPreFilters, selectedPreFilters]
  )

  const isRefreshRequired =
    !isEqual(selectedPreFilters, appliedPreFilters) && wereBookingsRequested

  const downloadBookingsFilters = {
    ...selectedPreFilters,
    page: 1,
  }

  const downloadBookingsCSV = useCallback(
    async (filters: TPreFilters) => {
      setIsDownloadingCSV(true)
      const { isOk, message } = await getBookingsCSVFileAdapter(filters)

      if (!isOk) {
        notify.error(message)
      }

      setIsDownloadingCSV(false)
    },
    [notify, getBookingsCSVFileAdapter]
  )

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
          <div className="pre-filters-row">
            <div className="pre-filters-venue">
              <FilterByVenue
                isDisabled={isFiltersDisabled}
                selectedVenueId={selectedPreFilters.offerVenueId}
                updateFilters={updateSelectedFilters}
                venuesFormattedAndOrdered={venues}
              />
            </div>
            {!separateIndividualAndCollectiveOffers && (
              <div className="pre-filters-offer-type">
                <FilterByOfferType
                  isDisabled={isFiltersDisabled}
                  selectedOfferType={selectedPreFilters.offerType}
                  updateFilters={updateSelectedFilters}
                />
              </div>
            )}
            <FilterByEventDate
              isDisabled={isFiltersDisabled}
              selectedOfferDate={selectedPreFilters.offerEventDate}
              updateFilters={updateSelectedFilters}
            />
          </div>
          {!isBookingFiltersActive && (
            <FilterByBookingPeriod
              isDisabled={isFiltersDisabled}
              selectedBookingBeginningDate={
                selectedPreFilters.bookingBeginningDate
              }
              selectedBookingEndingDate={selectedPreFilters.bookingEndingDate}
              updateFilters={updateSelectedFilters}
            />
          )}
          {isBookingFiltersActive && (
            <div className="pre-filters-row">
              <FilterByBookingStatusPeriod
                isDisabled={isFiltersDisabled}
                selectedBookingBeginningDate={
                  selectedPreFilters.bookingBeginningDate
                }
                selectedBookingEndingDate={selectedPreFilters.bookingEndingDate}
                selectedBookingFilter={selectedPreFilters.bookingStatusFilter}
                updateFilters={updateSelectedFilters}
              />
            </div>
          )}
        </div>
        <div className="button-group">
          <span className="button-group-separator" />
          <div className="button-group-buttons">
            <button
              className="primary-button"
              disabled={isDownloadingCSV || isLocalLoading || isFiltersDisabled}
              onClick={() => downloadBookingsCSV(downloadBookingsFilters)}
              type="button"
            >
              Télécharger
            </button>
            <button
              className="secondary-button"
              disabled={isTableLoading || isLocalLoading || isFiltersDisabled}
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
          Vos filtres ont été modifiés. Veuillez cliquer sur « Afficher » pour
          actualiser votre recherche.
        </p>
      )}
    </>
  )
}

export default PreFilters
