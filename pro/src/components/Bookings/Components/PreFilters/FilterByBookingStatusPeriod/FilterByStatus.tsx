import type { BookingStatusFilter } from '@/apiClient/v1'
import { BOOKING_STATUS_FILTER_OPTIONS } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './FilterByBookingStatusPeriod.module.scss'

interface FilterByStatusProps {
  isDisabled: boolean
  updateFilters: (filters: Partial<PreFiltersParams>) => void
  selectedStatusId: string
}

export const FilterByStatus = ({
  isDisabled = false,
  updateFilters,
  selectedStatusId,
}: FilterByStatusProps): JSX.Element => (
  <>
    <Select
      onChange={(event) =>
        updateFilters({
          bookingStatusFilter: event.target.value as BookingStatusFilter,
        })
      }
      disabled={isDisabled}
      name="statusFilter"
      className={styles['status-filter']}
      options={BOOKING_STATUS_FILTER_OPTIONS}
      value={selectedStatusId}
      ariaLabel={'Type de période'}
      label=""
    />
  </>
)
