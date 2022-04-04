import React from 'react'

import Select from 'components/layout/inputs/Select'
import { BOOOKING_STATUS_FILTER, DEFAULT_BOOKING_FILTER } from 'core/Bookings'

interface IPreFiltersProp {
  bookingBeginningDate: Date
  bookingEndingDate: Date
  bookingStatusFilter: string
  offerEventDate: Date
  offerVenueId: string
}

interface IFilterByStatusProps {
  isDisabled: boolean
  updateFilters: (filters: Partial<IPreFiltersProp>) => void
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
    updateFilters({ bookingStatusFilter: event.target.value })
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
