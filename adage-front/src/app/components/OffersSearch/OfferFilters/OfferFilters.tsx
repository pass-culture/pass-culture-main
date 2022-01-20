import React, { useState } from 'react'

import { Option } from 'app/types'
import { VenueFilterType } from 'utils/types'

import MultiSelectAutocomplete from '../../../ui-kit/MultiSelectAutoComplete'
import SearchButton from '../../../ui-kit/SearchButton'

import { departmentOptions } from './departmentOptions'
import OfferFiltersTags from './OfferFiltersTags'
import './OfferFilters.scss'
import { studentsOptions } from './studentsOptions'

export const OfferFilters = ({
  className,
  handleSearchButtonClick,
  venueFilter,
  removeVenueFilter,
  isLoading,
}: {
  className?: string
  handleSearchButtonClick: (departments: Option[], students: Option[]) => void
  venueFilter: VenueFilterType | null
  removeVenueFilter: () => void
  isLoading: boolean
}): JSX.Element => {
  const [departments, setDepartments] = useState<Option[]>([])
  const [students, setStudents] = useState<Option[]>([])

  const handleDeleteFilter = (filterValue: string) => {
    setDepartments(
      departments.filter(department => department.value !== filterValue)
    )
    setStudents(students.filter(student => student.value !== filterValue))
  }

  const handleResetFilters = () => {
    removeVenueFilter()
    setDepartments([])
    setStudents([])
  }

  return (
    <div className={className}>
      <span className="offer-filters-title">Filter par :</span>
      <div className="offer-filters-row">
        <MultiSelectAutocomplete
          className="offer-filters-filter"
          initialValues={departments}
          label="Département"
          onChange={setDepartments}
          options={departmentOptions}
          pluralLabel="Départements"
        />
        <MultiSelectAutocomplete
          className="offer-filters-filter"
          initialValues={students}
          label="Niveau scolaire"
          onChange={setStudents}
          options={studentsOptions}
          pluralLabel="Niveaux scolaires"
        />
      </div>
      <OfferFiltersTags
        departments={departments}
        handleDeleteFilter={handleDeleteFilter}
        handleResetFilters={handleResetFilters}
        removeVenueFilter={removeVenueFilter}
        students={students}
        venueFilter={venueFilter}
      />
      <div className="offer-filters-button-container">
        <div className="offer-filters-button-separator" />
        <SearchButton
          disabled={isLoading}
          label="Lancer la recherche"
          onClick={() => handleSearchButtonClick(departments, students)}
        />
      </div>
    </div>
  )
}
