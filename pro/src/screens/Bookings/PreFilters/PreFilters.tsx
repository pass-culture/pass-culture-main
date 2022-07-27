import classNames from 'classnames'
import isEqual from 'lodash.isequal'
import React, { useCallback, useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'
import {
  DEFAULT_PRE_FILTERS,
  TPreFilters,
  GetBookingsCSVFileAdapter,
  GetBookingsXLSFileAdapter,
} from 'core/Bookings'
import { ReactComponent as ResetIcon } from 'icons/reset.svg'
import MultiDownloadButtonsModal from 'new_components/MultiDownloadButtonsModal/MultiDownloadButtonsModal'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { Events } from '../../../core/FirebaseEvents/constants'
import { RootState } from '../../../store/reducers'

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
  resetPreFilters: () => void
  urlParams?: TPreFilters
  updateUrl?: (selectedPreFilters: TPreFilters) => void
  venues: { id: string; displayName: string }[]
  getBookingsCSVFileAdapter: GetBookingsCSVFileAdapter
  getBookingsXLSFileAdapter: GetBookingsXLSFileAdapter
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
  resetPreFilters,
  venues,
  updateUrl,
  getBookingsCSVFileAdapter,
  getBookingsXLSFileAdapter,
}: IPreFiltersProps): JSX.Element => {
  const notify = useNotification()

  const isCsvMultiDownloadFiltersActive = useActiveFeature(
    'ENABLE_CSV_MULTI_DOWNLOAD_BUTTON'
  )

  const logEvent = useSelector((state: RootState) => state.app.logEvent)

  const [selectedPreFilters, setSelectedPreFilters] = useState<TPreFilters>({
    ...appliedPreFilters,
  })
  const [isDownloadingCSV, setIsDownloadingCSV] = useState<boolean>(false)

  useEffect(
    () => setSelectedPreFilters({ ...appliedPreFilters }),
    [appliedPreFilters]
  )

  const [hasPreFilters, setHasPreFilters] = useState<boolean>(false)
  useEffect(() => {
    let key: keyof TPreFilters
    let hasFilters = false
    for (key in selectedPreFilters) {
      if (selectedPreFilters[key] !== DEFAULT_PRE_FILTERS[key])
        hasFilters = true
    }
    setHasPreFilters(hasFilters)
  }, [selectedPreFilters])

  const updateSelectedFilters = useCallback(
    (updatedFilter: any) => {
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
    (event: any) => {
      event.preventDefault()
      applyPreFilters(selectedPreFilters)
      if (updateUrl) {
        updateUrl(selectedPreFilters)
      }
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
    async (filters: TPreFilters, type: string) => {
      setIsDownloadingCSV(true)

      const { isOk, message } =
        type === 'CSV'
          ? await getBookingsCSVFileAdapter(filters)
          : await getBookingsXLSFileAdapter(filters)

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
        <div className="reset-filters">
          <Button
            Icon={ResetIcon}
            disabled={!hasPreFilters}
            onClick={resetPreFilters}
            variant={ButtonVariant.TERNARY}
          >
            Réinitialiser les filtres
          </Button>
        </div>
        <div className="button-group">
          <span className="button-group-separator" />
          <div className="button-group-buttons">
            {isCsvMultiDownloadFiltersActive ? (
              <MultiDownloadButtonsModal
                downloadFunction={downloadBookingsCSV}
                filters={downloadBookingsFilters}
                isDownloading={isDownloadingCSV}
                isFiltersDisabled={isFiltersDisabled}
                isLocalLoading={isLocalLoading}
              />
            ) : (
              <button
                className="primary-button"
                disabled={
                  isDownloadingCSV || isLocalLoading || isFiltersDisabled
                }
                onClick={() =>
                  downloadBookingsCSV(downloadBookingsFilters, 'CSV')
                }
                type="button"
              >
                Télécharger
              </button>
            )}
            <Button
              disabled={isTableLoading || isLocalLoading || isFiltersDisabled}
              variant={ButtonVariant.SECONDARY}
              onClick={() => {
                updateUrl && updateUrl(selectedPreFilters)
                logEvent(Events.CLICKED_SHOW_BOOKINGS, {
                  from: location.pathname,
                })
              }}
            >
              Afficher
            </Button>
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
