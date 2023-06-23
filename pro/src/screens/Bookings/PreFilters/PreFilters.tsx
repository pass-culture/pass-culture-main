import classNames from 'classnames'
import isEqual from 'lodash.isequal'
import React, { useCallback, useEffect, useState } from 'react'

import FormLayout from 'components/FormLayout/FormLayout'
import MultiDownloadButtonsModal from 'components/MultiDownloadButtonsModal/MultiDownloadButtonsModal'
import {
  DEFAULT_PRE_FILTERS,
  GetBookingsCSVFileAdapter,
  GetBookingsXLSFileAdapter,
  TPreFilters,
} from 'core/Bookings'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { ReactComponent as RefreshIcon } from 'icons/full-refresh.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { Events } from '../../../core/FirebaseEvents/constants'

import FilterByBookingStatusPeriod from './FilterByBookingStatusPeriod'
import FilterByEventDate from './FilterByEventDate'
import FilterByVenue from './FilterByVenue'
import styles from './PreFilters.module.scss'

export interface PreFiltersProps {
  appliedPreFilters: TPreFilters
  applyPreFilters: (filters: TPreFilters) => void
  hasResult: boolean
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
  isFiltersDisabled,
  isTableLoading,
  wereBookingsRequested,
  isLocalLoading,
  resetPreFilters,
  venues,
  updateUrl,
  getBookingsCSVFileAdapter,
  getBookingsXLSFileAdapter,
}: PreFiltersProps): JSX.Element => {
  const notify = useNotification()

  const { logEvent } = useAnalytics()

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
      if (
        key.includes('Date') &&
        selectedPreFilters[key] instanceof Date &&
        DEFAULT_PRE_FILTERS[key] instanceof Date
      ) {
        if (
          // @ts-expect-error
          selectedPreFilters[key].getTime() !==
          // @ts-expect-error
          DEFAULT_PRE_FILTERS[key].getTime()
        ) {
          hasFilters = true
        }
      } else if (selectedPreFilters[key] !== DEFAULT_PRE_FILTERS[key]) {
        hasFilters = true
      }
    }
    setHasPreFilters(hasFilters)
  }, [selectedPreFilters])

  const updateSelectedFilters = useCallback(
    (updatedFilter: any) => {
      if (updatedFilter.offerEventDate) {
        updatedFilter.bookingBeginningDate = null
        updatedFilter.bookingEndingDate = null
        /* istanbul ignore next: DEBT to fix */
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
    /* istanbul ignore next: DEBT to fix */
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

      /* istanbul ignore next: DEBT to fix */
      const { isOk, message } =
        type === 'CSV'
          ? await getBookingsCSVFileAdapter(filters)
          : await getBookingsXLSFileAdapter(filters)

      /* istanbul ignore next: DEBT to fix */
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
        className={classNames(styles['pre-filters-form'], {
          [styles['has-result']]: hasResult,
          [styles['refresh-required']]: isRefreshRequired,
        })}
        onSubmit={requestFilteredBookings}
      >
        <div>
          <FormLayout.Row inline>
            <FilterByVenue
              isDisabled={isFiltersDisabled}
              selectedVenueId={selectedPreFilters.offerVenueId}
              updateFilters={updateSelectedFilters}
              venuesFormattedAndOrdered={venues}
            />

            <FilterByEventDate
              isDisabled={isFiltersDisabled}
              selectedOfferDate={selectedPreFilters.offerEventDate}
              updateFilters={updateSelectedFilters}
            />
          </FormLayout.Row>

          <FormLayout.Row inline>
            <FilterByBookingStatusPeriod
              isDisabled={isFiltersDisabled}
              selectedBookingBeginningDate={
                selectedPreFilters.bookingBeginningDate
              }
              selectedBookingEndingDate={selectedPreFilters.bookingEndingDate}
              selectedBookingFilter={selectedPreFilters.bookingStatusFilter}
              updateFilters={updateSelectedFilters}
            />
          </FormLayout.Row>
        </div>

        <div className={styles['reset-filters']}>
          <Button
            Icon={RefreshIcon}
            disabled={!hasPreFilters}
            onClick={resetPreFilters}
            variant={ButtonVariant.TERNARY}
          >
            Réinitialiser les filtres
          </Button>
        </div>

        <div className="button-group">
          <div className="button-group-buttons">
            <span className="button-group-separator" />

            <MultiDownloadButtonsModal
              downloadFunction={downloadBookingsCSV}
              filters={downloadBookingsFilters}
              isDownloading={isDownloadingCSV}
              isFiltersDisabled={isFiltersDisabled}
              isLocalLoading={isLocalLoading}
            />

            <Button
              className={styles['show-button']}
              disabled={isTableLoading || isLocalLoading || isFiltersDisabled}
              variant={ButtonVariant.SECONDARY}
              onClick={() => {
                updateUrl && updateUrl(selectedPreFilters)
                logEvent?.(Events.CLICKED_SHOW_BOOKINGS, {
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
          className={styles['pf-refresh-message']}
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
