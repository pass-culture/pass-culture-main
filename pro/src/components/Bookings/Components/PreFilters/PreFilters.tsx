import classNames from 'classnames'
import type { SubmitEvent } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { ALL_OFFERER_ADDRESS_OPTION } from '@/commons/core/Offers/constants'
import type { SelectOption } from '@/commons/custom_types/form'
import { isDateValid } from '@/commons/utils/date'
import { DownloadDropdown } from '@/components/DownloadDropdown/DownloadDropdown'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { Select } from '@/ui-kit/form/Select/Select'

import { FilterByBookingStatusPeriod } from './FilterByBookingStatusPeriod/FilterByBookingStatusPeriod'
import styles from './PreFilters.module.scss'

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
  offererAddresses: SelectOption<string | number>[]
  download?: (type: 'CSV' | 'XLS') => Promise<void>
  isDownloading?: boolean
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
  download,
  isDownloading,
}: PreFiltersProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  const requestFilteredBookings = (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault()
    applyNow()
  }

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

        {isAdministrationSpace && download && (
          <DownloadDropdown
            isDisabled={isDownloading || isFiltersDisabled || isLocalLoading}
            label="Télécharger les réservations"
            logEventNames={{
              onSelectCsv: Events.CLICKED_ADMIN_DOWNLOAD_BOOKINGS_CSV,
              onSelectXls: Events.CLICKED_ADMIN_DOWNLOAD_BOOKINGS_XLS,
              onToggle: Events.CLICKED_ADMIN_DOWNLOAD_BOOKINGS,
            }}
            onSelect={download}
          />
        )}
        <div className={styles['button-group']}>
          <div className={styles['button-group-buttons']}>
            {!isAdministrationSpace && (
              <Button
                disabled={isTableLoading || isLocalLoading || isFiltersDisabled}
                variant={ButtonVariant.PRIMARY}
                onClick={() => {
                  applyNow()
                  logEvent('CLICKED_SHOW_BOOKINGS', { from: location.pathname })
                }}
                label="Rechercher les réservations"
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
