import {
  BOOOKING_STATUS_FILTER,
  DEFAULT_BOOKING_FILTER,
  TPreFilters,
} from 'core/Bookings'

import { BookingStatusFilter } from 'apiClient/v1'
import React from 'react'
import Select from 'components/layout/inputs/Select'

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
