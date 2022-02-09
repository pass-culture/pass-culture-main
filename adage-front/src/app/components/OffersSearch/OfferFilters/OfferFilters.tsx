import isEqual from 'lodash/isEqual'
import React, { useEffect, useState } from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import { getEducationalCategoriesOptionsAdapter } from 'app/adapters/getEducationalCategoriesOptionsAdapter'
import { Option } from 'app/types'
import { VenueFilterType } from 'utils/types'

import { Button, MultiSelectAutocomplete } from '../../../ui-kit'

import { departmentOptions } from './departmentOptions'
import OfferFiltersTags from './OfferFiltersTags'
import './OfferFilters.scss'
import { studentsOptions } from './studentsOptions'

interface OfferFiltersProps {
  className?: string
  handleSearchButtonClick: (
    departments: Option[],
    categories: Option<string[]>[],
    students: Option[]
  ) => void
  venueFilter: VenueFilterType | null
  removeVenueFilter: () => void
  isLoading: boolean
  query: string
  refine: SearchBoxProvided['refine']
}

export const OfferFilters = ({
  className,
  handleSearchButtonClick,
  venueFilter,
  removeVenueFilter,
  isLoading,
  refine,
  query,
}: OfferFiltersProps): JSX.Element => {
  const [departments, setDepartments] = useState<Option[]>([])
  const [categories, setCategories] = useState<Option<string[]>[]>([])
  const [students, setStudents] = useState<Option[]>([])

  const [categoriesOptions, setCategoriesOptions] = useState<
    Option<string[]>[]
  >([])

  const handleDeleteFilter = (filterValue: string | string[]) => {
    if (typeof filterValue === 'string') {
      setDepartments(
        departments.filter(department => department.value !== filterValue)
      )
      setStudents(students.filter(student => student.value !== filterValue))
    } else {
      setCategories(
        categories.filter(category => !isEqual(category.value, filterValue))
      )
    }
  }

  const handleResetFilters = () => {
    removeVenueFilter()
    setDepartments([])
    setCategories([])
    setStudents([])
  }

  useEffect(() => {
    const loadSubCategoriesOptions = async () => {
      const { payload, isOk } = await getEducationalCategoriesOptionsAdapter(
        null
      )

      if (isOk) {
        setCategoriesOptions(payload.educationalCategories)
      }
    }

    loadSubCategoriesOptions()
  }, [])

  return (
    <div className={className}>
      <span className="offer-filters-title">Filtrer par :</span>
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
          initialValues={categories}
          label="Catégorie"
          onChange={setCategories}
          options={categoriesOptions}
          pluralLabel="Catégories"
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
        categories={categories}
        departments={departments}
        handleDeleteFilter={handleDeleteFilter}
        handleResetFilters={handleResetFilters}
        removeVenueFilter={removeVenueFilter}
        students={students}
        venueFilter={venueFilter}
      />
      <div className="offer-filters-button-container">
        <div className="offer-filters-button-separator" />
        <Button
          disabled={isLoading}
          label="Lancer la recherche"
          onClick={() => {
            handleSearchButtonClick(departments, categories, students)
            refine(query)
          }}
        />
      </div>
    </div>
  )
}
