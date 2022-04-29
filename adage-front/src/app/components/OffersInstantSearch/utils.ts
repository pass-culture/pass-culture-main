import flatMap from 'lodash/flatMap'

import { LEGACY_INITIAL_FACET_FILTERS } from 'app/constants'
import { Facets, Option } from 'app/types'
import { VenueFilterType } from 'app/types/offers'

export const populateFacetFilters = ({
  departments,
  categories,
  students,
  venueFilter = null,
}: {
  departments: Option[]
  categories: Option<string[]>[]
  students: Option[]
  venueFilter: VenueFilterType | null
}): Facets => {
  const updatedFilters: Facets = [...LEGACY_INITIAL_FACET_FILTERS]
  const filteredDepartments: string[] = departments.map(
    department => `venue.departmentCode:${department.value}`
  )
  const filteredCategories: string[] = flatMap(
    categories,
    (category: Option<string[]>) =>
      // category.value contains all subcategoryIds for this category
      category.value.map(
        subcategoryId => `offer.subcategoryId:${subcategoryId}`
      )
  )
  const filteredStudents: string[] = students.map(
    student => `offer.students:${student.value}`
  )

  if (filteredDepartments.length > 0) {
    updatedFilters.push(filteredDepartments)
  }
  if (filteredCategories.length > 0) {
    updatedFilters.push(filteredCategories)
  }
  if (filteredStudents.length > 0) {
    updatedFilters.push(filteredStudents)
  }

  if (venueFilter?.id) {
    updatedFilters.push(`venue.id:${venueFilter.id}`)
  }

  return updatedFilters
}
