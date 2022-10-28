import React from 'react'

import { BookingStatusFilter } from 'apiClient/v1'
import {
  BOOOKING_STATUS_FILTER,
  DEFAULT_BOOKING_FILTER,
  TPreFilters,
} from 'core/Bookings'
import Select from 'ui-kit/form_raw/Select'

interface IFilterByStatusProps {
  isDisabled: boolean
  updateFilters: (filters: Partial<TPreFilters>) => void
  selectedStatusId: string
}

const FilterByStatus = ({
  isDisabled = false,
  updateFilters,
  selectedStatusId,
}: IFilterByStatusProps): JSX.Element => {
  function handleStatusFilterSelection(
    event: React.ChangeEvent<HTMLSelectElement>
  ) {
    updateFilters({
      bookingStatusFilter: event.target.value as BookingStatusFilter,
    })
  }

  return (
    <Select
      defaultOption={DEFAULT_BOOKING_FILTER}
      handleSelection={handleStatusFilterSelection}
      isDisabled={isDisabled}
      name="statusFilter"
      options={BOOOKING_STATUS_FILTER}
      selectedValue={selectedStatusId}
    />
  )
}

export default FilterByStatus
