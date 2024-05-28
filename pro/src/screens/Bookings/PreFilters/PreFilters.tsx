import classNames from 'classnames'
import isEqual from 'lodash.isequal'
import React, { FormEvent, useCallback, useEffect, useState } from 'react'

import useAnalytics from 'app/App/analytics/firebase'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { MultiDownloadButtonsModal } from 'components/MultiDownloadButtonsModal/MultiDownloadButtonsModal'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { Audience } from 'core/shared/types'
import useNotification from 'hooks/useNotification'
import fullRefreshIcon from 'icons/full-refresh.svg'
import { downloadIndividualBookingsCSVFile } from 'pages/Bookings/downloadIndividualBookingsCSVFile'
import { downloadIndividualBookingsXLSFile } from 'pages/Bookings/downloadIndividualBookingsXLSFile'
import { downloadCollectiveBookingsCSVFile } from 'pages/CollectiveBookings/downloadCollectiveBookingsCSVFile'
import { downloadCollectiveBookingsXLSFile } from 'pages/CollectiveBookings/downloadCollectiveBookingsXLSFile'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { isDateValid } from 'utils/date'

import { Events } from '../../../core/FirebaseEvents/constants'

import { FilterByBookingStatusPeriod } from './FilterByBookingStatusPeriod/FilterByBookingStatusPeriod'
import { FilterByEventDate } from './FilterByEventDate'
import { FilterByVenue } from './FilterByVenue'
import styles from './PreFilters.module.scss'

export interface PreFiltersProps {
  appliedPreFilters: PreFiltersParams
  applyPreFilters: (filters: PreFiltersParams) => void
  audience: Audience
  hasResult: boolean
  isFiltersDisabled: boolean
  isTableLoading: boolean
  wereBookingsRequested: boolean
  isLocalLoading: boolean
  resetPreFilters: () => void
  urlParams?: PreFiltersParams
  updateUrl?: (selectedPreFilters: PreFiltersParams) => void
  venues: { id: string; displayName: string }[]
}

export const PreFilters = ({
  appliedPreFilters,
  applyPreFilters,
  audience,
  hasResult,
  isFiltersDisabled,
  isTableLoading,
  wereBookingsRequested,
  isLocalLoading,
  resetPreFilters,
  venues,
  updateUrl,
}: PreFiltersProps): JSX.Element => {
  const notify = useNotification()

  const { logEvent } = useAnalytics()

  const [selectedPreFilters, setSelectedPreFilters] =
    useState<PreFiltersParams>({
      ...appliedPreFilters,
    })
  const [isDownloadingCSV, setIsDownloadingCSV] = useState<boolean>(false)

  useEffect(
    () => setSelectedPreFilters({ ...appliedPreFilters }),
    [appliedPreFilters]
  )

  const [hasPreFilters, setHasPreFilters] = useState<boolean>(false)
  useEffect(() => {
    let key: keyof PreFiltersParams
    let hasFilters = false
    for (key in selectedPreFilters) {
      const selectedValue = selectedPreFilters[key]
      const defaultValue = DEFAULT_PRE_FILTERS[key]
      if (
        key.includes('Date') &&
        isDateValid(selectedValue) &&
        isDateValid(defaultValue)
      ) {
        if (
          new Date(selectedValue).getTime() !== new Date(defaultValue).getTime()
        ) {
          hasFilters = true
        }
      } else if (selectedValue !== defaultValue) {
        hasFilters = true
      }
    }
    setHasPreFilters(hasFilters)
  }, [selectedPreFilters])

  const updateSelectedFilters = useCallback(
    (updatedFilter: any) => {
      if (updatedFilter.offerEventDate) {
        updatedFilter.bookingBeginningDate = ''
        updatedFilter.bookingEndingDate = ''
        /* istanbul ignore next: DEBT to fix */
        if (updatedFilter.offerEventDate === appliedPreFilters.offerEventDate) {
          updatedFilter.bookingBeginningDate =
            appliedPreFilters.bookingBeginningDate
          updatedFilter.bookingEndingDate = appliedPreFilters.bookingEndingDate
        }
      }

      setSelectedPreFilters((currentFilters) => ({
        ...currentFilters,
        ...updatedFilter,
      }))
    },
    [appliedPreFilters]
  )

  const requestFilteredBookings = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    applyPreFilters(selectedPreFilters)
    if (updateUrl) {
      updateUrl(selectedPreFilters)
    }
  }

  const isRefreshRequired =
    !isEqual(selectedPreFilters, appliedPreFilters) && wereBookingsRequested

  const downloadBookingsFilters = {
    ...selectedPreFilters,
    page: 1,
  }

  const downloadBookingsCSV = useCallback(
    async (filters: PreFiltersParams, type: string) => {
      setIsDownloadingCSV(true)

      try {
        if (audience === Audience.INDIVIDUAL) {
          /* istanbul ignore next: DEBT to fix */
          if (type === 'CSV') {
            await downloadIndividualBookingsCSVFile(filters)
          } else {
            await downloadIndividualBookingsXLSFile(filters)
          }
        } else {
          if (type === 'CSV') {
            await downloadCollectiveBookingsCSVFile(filters)
          } else {
            await downloadCollectiveBookingsXLSFile(filters)
          }
        }
      } catch {
        notify.error(GET_DATA_ERROR_MESSAGE)
      }

      setIsDownloadingCSV(false)
    },
    [notify, audience]
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
            icon={fullRefreshIcon}
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
