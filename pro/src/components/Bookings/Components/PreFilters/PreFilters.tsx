import classNames from 'classnames'
import { type SubmitEvent, useCallback, useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { ALL_OFFERER_ADDRESS_OPTION } from '@/commons/core/Offers/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import type { SelectOption } from '@/commons/custom_types/form'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { isDateValid } from '@/commons/utils/date'
import { DownloadDropdown } from '@/components/DownloadDropdown/DownloadDropdown'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { Select } from '@/ui-kit/form/Select/Select'

import { MovedBookingDownloadWarningModal } from '../MovedBookingDownloadWarningModal/MovedBookingDownloadWarningModal'
import { FilterByBookingStatusPeriod } from './FilterByBookingStatusPeriod/FilterByBookingStatusPeriod'
import styles from './PreFilters.module.scss'
import { downloadIndividualBookingsCSVFile } from './utils/downloadIndividualBookingsCSVFile'
import { downloadIndividualBookingsXLSFile } from './utils/downloadIndividualBookingsXLSFile'

export interface PreFiltersProps {
  selectedPreFilters: PreFiltersParams
  updateSelectedFilters: (updated: Partial<PreFiltersParams>) => void
  hasPreFilters: boolean
  isRefreshRequired: boolean
  applyNow: () => void

  hasResult: boolean
  isFiltersDisabled?: boolean
  isTableLoading: boolean
  wereBookingsRequested: boolean
  isAdministrationSpace?: boolean
  isLocalLoading: boolean
  resetPreFilters: () => void
  urlParams?: PreFiltersParams
  updateUrl: (selectedPreFilters: PreFiltersParams) => void
  offererAddresses: SelectOption[]
}

export const PreFilters = ({
  selectedPreFilters,
  updateSelectedFilters,
  hasPreFilters,
  isRefreshRequired,
  applyNow,
  hasResult,
  isAdministrationSpace = false,
  isFiltersDisabled = false,
  isTableLoading,
  isLocalLoading,
  resetPreFilters,
  offererAddresses,
}: PreFiltersProps): JSX.Element => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()

  const [isDownloading, setIsDownloading] = useState(false)

  const requestFilteredBookings = (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault()
    applyNow()
  }

  const download = useCallback(
    async (type: 'CSV' | 'XLS') => {
      setIsDownloading(true)

      const filters = { ...selectedPreFilters, page: 1 }

      try {
        /* istanbul ignore next: DEBT to fix */
        if (type === 'CSV') {
          await downloadIndividualBookingsCSVFile(filters)
        } else {
          await downloadIndividualBookingsXLSFile(filters)
        }
      } catch {
        snackBar.error(GET_DATA_ERROR_MESSAGE)
      }

      setIsDownloading(false)
    },
    [selectedPreFilters, snackBar]
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
        <div
          className={classNames(styles['pre-filters-form-filters'], {
            [styles['single-row']]: isAdministrationSpace,
          })}
        >
          <FormLayout.Row inline mdSpaceAfter>
            {!isAdministrationSpace && (
              <Select
                className={styles['venue-filter']}
                label="Localisation"
                defaultOption={ALL_OFFERER_ADDRESS_OPTION}
                onChange={(e) =>
                  updateSelectedFilters({ offererAddressId: e.target.value })
                }
                disabled={isFiltersDisabled}
                name="address"
                options={offererAddresses}
                value={selectedPreFilters.offererAddressId}
              />
            )}

            <DatePicker
              label="Date de l’évènement"
              className={styles['offer-date-filter']}
              required={false}
              name="select-filter-date"
              onChange={(event) =>
                updateSelectedFilters({
                  offerEventDate:
                    event.target.value === ''
                      ? DEFAULT_PRE_FILTERS.offerEventDate
                      : event.target.value,
                })
              }
              disabled={isFiltersDisabled}
              value={
                isDateValid(selectedPreFilters.offerEventDate)
                  ? selectedPreFilters.offerEventDate
                  : ''
              }
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

            <div className={styles['reset-filters-wrapper']}>
              <Button
                icon={fullRefreshIcon}
                disabled={!hasPreFilters}
                onClick={resetPreFilters}
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                type="button"
                label="Réinitialiser les filtres"
              />
            </div>
          </FormLayout.Row>
        </div>

        {isAdministrationSpace && (
          <DownloadDropdown
            isDisabled={isDownloading || isFiltersDisabled || isLocalLoading}
            label="Télécharger les réservations"
            logEventNames={{
              onSelectCsv: Events.CLICKED_DOWNLOAD_BOOKINGS_CSV,
              onSelectXls: Events.CLICKED_DOWNLOAD_BOOKINGS_XLS,
              onToggle: Events.CLICKED_DOWNLOAD_BOOKINGS,
            }}
            onSelect={download}
          />
        )}
        <div className={styles['button-group']}>
          <div className={styles['button-group-buttons']}>
            {!withSwitchVenueFeature && (
              <DownloadDropdown
                isDisabled={
                  isDownloading || isFiltersDisabled || isLocalLoading
                }
                logEventNames={{
                  onSelectCsv: Events.CLICKED_DOWNLOAD_BOOKINGS_CSV,
                  onSelectXls: Events.CLICKED_DOWNLOAD_BOOKINGS_XLS,
                  onToggle: Events.CLICKED_DOWNLOAD_BOOKINGS,
                }}
                onSelect={download}
                title="Télécharger les réservations"
              />
            )}
            {withSwitchVenueFeature && !isAdministrationSpace && (
              <MovedBookingDownloadWarningModal />
            )}

            {!isAdministrationSpace && (
              <Button
                disabled={isTableLoading || isLocalLoading || isFiltersDisabled}
                variant={ButtonVariant.SECONDARY}
                onClick={() => {
                  applyNow()
                  logEvent('CLICKED_SHOW_BOOKINGS', { from: location.pathname })
                }}
                label="Afficher"
              />
            )}
          </div>

          {!isAdministrationSpace && (
            <span className={styles['button-group-separator']} />
          )}
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
