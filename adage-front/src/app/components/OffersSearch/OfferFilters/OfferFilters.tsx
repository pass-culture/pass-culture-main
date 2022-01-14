import React, { useState } from 'react'

import { Option } from 'app/types'
import { VenueFilterType } from 'utils/types'

import MultiSelectAutocomplete from '../../../ui-kit/MultiSelectAutoComplete'

import { departmentOptions } from './departmentOptions'
import OfferFiltersTags from './OfferFiltersTags'

import './OfferFilters.scss'

export const OfferFilters = ({
  className,
  venueFilter,
  removeVenueFilter,
}: {
  className?: string
  venueFilter: VenueFilterType | null
  removeVenueFilter: () => void
}): JSX.Element => {
  // to delete when departments is used
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [departments, setDepartments] = useState<Option[]>([])

  const onMultiSelectChange = (selectedOptions: Option[]): void => {
    setDepartments(selectedOptions)
  }

  const handleDeleteFilter = (filterValue: string) => {
    setDepartments(
      departments.filter(department => department.value !== filterValue)
    )
  }

  const handleResetFilters = () => {
    removeVenueFilter()
    setDepartments([])
  }

  return (
    <div className={className}>
      <span className="offer-filters-title">Filter par :</span>
      <MultiSelectAutocomplete
        initialValues={departments}
        label="Département"
        onChange={onMultiSelectChange}
        options={departmentOptions}
      />
      <OfferFiltersTags
        departments={departments}
        handleDeleteFilter={handleDeleteFilter}
        handleResetFilters={handleResetFilters}
        removeVenueFilter={removeVenueFilter}
        venueFilter={venueFilter}
      />
    </div>
  )
}
