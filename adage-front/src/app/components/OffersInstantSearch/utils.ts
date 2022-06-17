import flatMap from 'lodash/flatMap'

import { VenueResponse } from 'api/gen'
import { Facets, Option } from 'app/types'

export const populateFacetFilters = ({
  departments,
  categories,
  students,
  domains,
  venueFilter = null,
  uai,
}: {
  departments: Option[]
  categories: Option<string[]>[]
  students: Option[]
  domains: Option<number>[]
  venueFilter: VenueResponse | null
  uai?: string | null
}): Facets => {
  const updatedFilters: Facets = []
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
  const filteredDomains: string[] = domains.map(
    domain => `offer.domains:${domain.value}`
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
  if (filteredDomains.length > 0) {
    updatedFilters.push(filteredDomains)
  }

  if (venueFilter?.id) {
    updatedFilters.push(`venue.id:${venueFilter.id}`)
  }

  if (uai) {
    updatedFilters.push(`offer.educationalInstitutionUAICode:${uai}`)
  }

  return updatedFilters
}
