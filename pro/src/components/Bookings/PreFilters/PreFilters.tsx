import { useAnalytics } from 'app/App/analytics/firebase'
import classNames from 'classnames'
import { DEFAULT_PRE_FILTERS } from 'commons/core/Bookings/constants'
import {
  CollectivePreFiltersParams,
  PreFiltersParams,
} from 'commons/core/Bookings/types'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { ALL_OFFERER_ADDRESS_OPTION } from 'commons/core/Offers/constants'
import { GET_DATA_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { Audience } from 'commons/core/shared/types'
import { SelectOption } from 'commons/custom_types/form'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { isDateValid } from 'commons/utils/date'
import { isEqual } from 'commons/utils/isEqual'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { MultiDownloadButtonsModal } from 'components/MultiDownloadButtonsModal/MultiDownloadButtonsModal'
import fullRefreshIcon from 'icons/full-refresh.svg'
import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SelectInput } from 'ui-kit/form/shared/BaseSelectInput/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import { FilterByBookingStatusPeriod } from './FilterByBookingStatusPeriod/FilterByBookingStatusPeriod'
import { FilterByEventDate } from './FilterByEventDate'
import { FilterByVenue } from './FilterByVenue'
import styles from './PreFilters.module.scss'
import { downloadCollectiveBookingsCSVFile } from './utils/downloadCollectiveBookingsCSVFile'
import { downloadCollectiveBookingsXLSFile } from './utils/downloadCollectiveBookingsXLSFile'
import { downloadIndividualBookingsCSVFile } from './utils/downloadIndividualBookingsCSVFile'
import { downloadIndividualBookingsXLSFile } from './utils/downloadIndividualBookingsXLSFile'

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
  updateUrl: (selectedPreFilters: PreFiltersParams) => void
  venues: { id: string; displayName: string }[]
  offererAddresses: SelectOption[]
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
  offererAddresses,
  updateUrl,
}: PreFiltersProps): JSX.Element => {
  const notify = useNotification()

  const { logEvent } = useAnalytics()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const initialAppliedFilters = {
    ...DEFAULT_PRE_FILTERS,
    ...{
      offererId: selectedOffererId?.toString(),
    },
  }

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
      const defaultValue = initialAppliedFilters[key]
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
    updateUrl(selectedPreFilters)
  }

  const isRefreshRequired =
    !isEqual(selectedPreFilters, appliedPreFilters) && wereBookingsRequested

  const downloadBookingsFilters = {
    ...selectedPreFilters,
    page: 1,
  }

  type DownloadParams =
    | { audience: Audience.INDIVIDUAL; filters: PreFiltersParams }
    | {
        audience: Audience.COLLECTIVE
        filters: CollectivePreFiltersParams
      }
  const downloadBookingsCSV = useCallback(
    async ({ audience, filters }: DownloadParams, type: 'CSV' | 'XLS') => {
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
        <div className={styles['pre-filters-form-filters']}>
          <FormLayout.Row inline>
            {audience === Audience.INDIVIDUAL ? (
              <FieldLayout
                label="Localisation"
                name="address"
                className={styles['venue-filter']}
                isOptional
              >
                <SelectInput
                  defaultOption={ALL_OFFERER_ADDRESS_OPTION}
                  onChange={(event) =>
                    updateSelectedFilters({
                      offererAddressId: event.target.value,
                    })
                  }
                  disabled={isFiltersDisabled}
                  name="address"
                  options={offererAddresses}
                  value={selectedPreFilters.offererAddressId}
                />
              </FieldLayout>
            ) : (
              <FilterByVenue
                isDisabled={isFiltersDisabled}
                selectedVenueId={selectedPreFilters.offerVenueId}
                updateFilters={updateSelectedFilters}
                venuesFormattedAndOrdered={venues}
              />
            )}

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
                downloadBookingsCSV(
                  { audience, filters } as DownloadParams,
                  type
                )
              }
              filters={downloadBookingsFilters}
              isDownloading={isDownloadingCSV}
              isFiltersDisabled={isFiltersDisabled}
              isLocalLoading={isLocalLoading}
              className={styles['download-button']}
            />
            <Button
              className={styles['show-button']}
              disabled={isTableLoading || isLocalLoading || isFiltersDisabled}
              variant={ButtonVariant.SECONDARY}
              onClick={() => {
                updateUrl(selectedPreFilters)
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
