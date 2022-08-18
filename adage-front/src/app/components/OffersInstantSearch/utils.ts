import flatMap from 'lodash/flatMap'

import { VenueResponse } from 'apiClient'
import { Facets, Option } from 'app/types'

export const populateFacetFilters = ({
  departments,
  categories,
  students,
  domains,
  venueFilter = null,
  onlyInMySchool,
  uai,
  enableInterventionAreaFilter,
}: {
  departments: Option[]
  categories: Option<string[]>[]
  students: Option[]
  domains: Option<number>[]
  venueFilter: VenueResponse | null
  onlyInMySchool: boolean
  uai?: string[] | null
  enableInterventionAreaFilter: boolean
}): Facets => {
  const updatedFilters: Facets = []

  const filteredDepartments: string[] = enableInterventionAreaFilter
    ? flatMap(departments, (department: Option<string>) => [
        `venue.departmentCode:${department.value}`,
        `offer.interventionArea:${department.value}`,
      ])
    : departments.map(department => `venue.departmentCode:${department.value}`)

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
    updatedFilters.push(
      uai.map(uaiCode => `offer.educationalInstitutionUAICode:${uaiCode}`)
    )
  }

  if (onlyInMySchool) {
    updatedFilters.push('offer.eventAddressType:school')
  }

  return updatedFilters
}
