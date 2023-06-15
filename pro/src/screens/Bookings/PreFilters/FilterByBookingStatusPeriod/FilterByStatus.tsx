import React from 'react'

import { BookingStatusFilter } from 'apiClient/v1'
import {
  BOOKING_STATUS_FILTER,
  DEFAULT_BOOKING_FILTER,
  TPreFilters,
} from 'core/Bookings'
import SelectInput from 'ui-kit/form/Select/SelectInput'

import styles from './FilterByBookingStatusPeriod.module.scss'

interface FilterByStatusProps {
  isDisabled: boolean
  updateFilters: (filters: Partial<TPreFilters>) => void
  selectedStatusId: string
}

const FilterByStatus = ({
  isDisabled = false,
  updateFilters,
  selectedStatusId,
}: FilterByStatusProps): JSX.Element => (
  <SelectInput
    defaultOption={DEFAULT_BOOKING_FILTER}
    onChange={event =>
      updateFilters({
        bookingStatusFilter: event.target.value as BookingStatusFilter,
      })
    }
    disabled={isDisabled}
    name="statusFilter"
    className={styles['status-filter']}
    options={BOOKING_STATUS_FILTER}
    value={selectedStatusId}
  />
)

export default FilterByStatus
