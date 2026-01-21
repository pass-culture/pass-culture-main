import type { BookingStatusFilter } from '@/apiClient/v1'
import { BOOKING_STATUS_FILTER_OPTIONS } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './FilterByBookingStatusPeriod.module.scss'

interface FilterByBookingStatusPeriodProps {
  isDisabled: boolean
  selectedBookingBeginningDate: string
  selectedBookingEndingDate: string
  selectedBookingFilter: string
  updateFilters: (filters: Partial<PreFiltersParams>) => void
}

export const FilterByBookingStatusPeriod = ({
  isDisabled = false,
  selectedBookingBeginningDate,
  selectedBookingEndingDate,
  selectedBookingFilter,
  updateFilters,
}: FilterByBookingStatusPeriodProps): JSX.Element => {
  const handleBookingBeginningDateChange = (bookingBeginningDate: string) => {
    updateFilters({ bookingBeginningDate })
  }

  const handleBookingEndingDateChange = (bookingEndingDate: string) => {
    updateFilters({ bookingEndingDate })
  }

  return (
    <fieldset className={styles['period-filter']}>
      <legend className={styles['visually-hidden']}>Période</legend>

      <Select
        className={styles['period-filter-status']}
        onChange={(event) =>
          updateFilters({
            bookingStatusFilter: event.target.value as BookingStatusFilter,
          })
        }
        disabled={isDisabled}
        name="statusFilter"
        options={BOOKING_STATUS_FILTER_OPTIONS}
        value={selectedBookingFilter}
        ariaLabel={'Type de période'}
        label=""
      />

      <PeriodSelector
        className={styles['period-filter-selector']}
        onBeginningDateChange={handleBookingBeginningDateChange}
        onEndingDateChange={handleBookingEndingDateChange}
        isDisabled={isDisabled}
        maxDateEnding={new Date()}
        periodBeginningDate={selectedBookingBeginningDate}
        periodEndingDate={selectedBookingEndingDate}
      />
    </fieldset>
  )
}
