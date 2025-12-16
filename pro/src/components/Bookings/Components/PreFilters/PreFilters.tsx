import classNames from 'classnames'
import { type FormEvent, useCallback, useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { ALL_OFFERER_ADDRESS_OPTION } from '@/commons/core/Offers/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import type { SelectOption } from '@/commons/custom_types/form'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MultiDownloadButtonsModal } from '@/components/MultiDownloadButtonsModal/MultiDownloadButtonsModal'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SelectInput } from '@/ui-kit/form/shared/BaseSelectInput/SelectInput'
import { FieldLayout } from '@/ui-kit/form/shared/FieldLayout/FieldLayout'

import { FilterByBookingStatusPeriod } from './FilterByBookingStatusPeriod/FilterByBookingStatusPeriod'
import { FilterByEventDate } from './FilterByEventDate'
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
  isFiltersDisabled: boolean
  isTableLoading: boolean
  wereBookingsRequested: boolean
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
  isFiltersDisabled,
  isTableLoading,
  isLocalLoading,
  resetPreFilters,
  offererAddresses,
}: PreFiltersProps): JSX.Element => {
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const [isDownloadingCSV, setIsDownloadingCSV] = useState(false)

  const requestFilteredBookings = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    applyNow()
  }

  const downloadBookingsFilters = { ...selectedPreFilters, page: 1 }

  const downloadBookingsCSV = useCallback(
    async (filters: PreFiltersParams, type: 'CSV' | 'XLS') => {
      setIsDownloadingCSV(true)

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

      setIsDownloadingCSV(false)
    },
    [snackBar]
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
        <div className={styles['pre-filters-form-filters']}>
          <FormLayout.Row inline>
            <FieldLayout
              label="Localisation"
              name="address"
              className={styles['venue-filter']}
              required={false}
            >
              <SelectInput
                defaultOption={ALL_OFFERER_ADDRESS_OPTION}
                onChange={(e) =>
                  updateSelectedFilters({ offererAddressId: e.target.value })
                }
                disabled={isFiltersDisabled}
                name="address"
                options={offererAddresses}
                value={selectedPreFilters.offererAddressId}
              />
            </FieldLayout>

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

            <div className={styles['reset-filters-wrapper']}>
              <Button
                icon={fullRefreshIcon}
                disabled={!hasPreFilters}
                onClick={resetPreFilters}
                variant={ButtonVariant.TERNARY}
                className={styles['reset-filters']}
              >
                Réinitialiser les filtres
              </Button>
            </div>
          </FormLayout.Row>
        </div>

        <div className={styles['button-group']}>
          <div className={styles['button-group-buttons']}>
            <span className={styles['button-group-separator']} />

            <MultiDownloadButtonsModal
              downloadFunction={(filters, type) =>
                downloadBookingsCSV(filters, type)
              }
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
                applyNow()
                logEvent('CLICKED_SHOW_BOOKINGS', { from: location.pathname })
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
