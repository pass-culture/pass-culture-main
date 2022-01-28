/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'

import Select from 'components/layout/inputs/Select'

import { BOOOKING_STATUS_FILTER, DEFAULT_BOOKING_FILTER } from '../_constants'

interface IPreFiltersProp {
  bookingBeginningDate: Date
  bookingEndingDate: Date
  bookingStatusFilter: string
  offerEventDate: Date
  offerVenueId: string
}

interface IFilterByStatusProps {
  updateFilters: (filters: Partial<IPreFiltersProp>) => void
  selectedStatusId: string
}
const FilterByStatus = ({
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
      name="statusFilter"
      options={BOOOKING_STATUS_FILTER}
      selectedValue={selectedStatusId}
    />
  )
}

FilterByStatus.propTypes = {
  selectedStatusId: PropTypes.string.isRequired,
  updateFilters: PropTypes.func.isRequired,
}

export default FilterByStatus
