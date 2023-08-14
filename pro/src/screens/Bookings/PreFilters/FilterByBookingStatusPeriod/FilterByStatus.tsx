import React from 'react'

import { BookingStatusFilter } from 'apiClient/v1'
import { BOOKING_STATUS_FILTER_OPTIONS } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import SelectInput from 'ui-kit/form/Select/SelectInput'

import styles from './FilterByBookingStatusPeriod.module.scss'

interface FilterByStatusProps {
  isDisabled: boolean
  updateFilters: (filters: Partial<PreFiltersParams>) => void
  selectedStatusId: string
}

const FilterByStatus = ({
  isDisabled = false,
  updateFilters,
  selectedStatusId,
}: FilterByStatusProps): JSX.Element => (
  <>
    <label className={styles['hidden-label']} id="period-type">
      Type de période
    </label>
    <SelectInput
      onChange={event =>
        updateFilters({
          bookingStatusFilter: event.target.value as BookingStatusFilter,
        })
      }
      disabled={isDisabled}
      name="statusFilter"
      className={styles['status-filter']}
      options={BOOKING_STATUS_FILTER_OPTIONS}
      value={selectedStatusId}
      ariaLabel="period-type"
    />
  </>
)

export default FilterByStatus
