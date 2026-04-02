import type { BookingEventType } from '@/apiClient/v1'
import { BOOKING_EVENT_TYPE_OPTIONS } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './FilterByBookingStatusPeriod.module.scss'

interface FilterByBookingStatusPeriodProps {
  isDisabled: boolean
  selectedBookingBeginningDate: string
  selectedBookingEndingDate: string
  selectedEventType: BookingEventType
  updateFilters: (filters: Partial<PreFiltersParams>) => void
}

export const FilterByBookingStatusPeriod = ({
  isDisabled = false,
  selectedBookingBeginningDate,
  selectedBookingEndingDate,
  selectedEventType,
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
        onChange={(event) =>
          updateFilters({
            eventType: event.target.value as BookingEventType,
          })
        }
        disabled={isDisabled}
        name="statusFilter"
        options={BOOKING_EVENT_TYPE_OPTIONS}
        value={selectedEventType}
        ariaLabel={'Type de période'}
        label=""
      />

      <PeriodSelector
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
