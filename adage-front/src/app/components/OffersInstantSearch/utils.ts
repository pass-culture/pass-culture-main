import flatMap from 'lodash/flatMap'

import { VenueResponse } from 'apiClient'
import { Facets, Option } from 'app/types'

interface FacetsWithData {
  queryFilters: Facets
  filtersKeys: string[]
}

export const populateFacetFilters = ({
  departments,
  categories,
  students,
  domains,
  venueFilter = null,
  onlyInMySchool,
  uai,
}: {
  departments: Option[]
  categories: Option<string[]>[]
  students: Option[]
  domains: Option<number>[]
  venueFilter: VenueResponse | null
  onlyInMySchool: boolean
  uai?: string[] | null
}): FacetsWithData => {
  const updatedFilters: Facets = []
  const filtersKeys: string[] = []

  const filteredDepartments: string[] = flatMap(
    departments,
    (department: Option<string>) => [
      `venue.departmentCode:${department.value}`,
      `offer.interventionArea:${department.value}`,
    ]
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
    filtersKeys.push('departments')
    filtersKeys.push('interventionArea')
    updatedFilters.push(filteredDepartments)
  }

  if (filteredCategories.length > 0) {
    filtersKeys.push('categories')
    updatedFilters.push(filteredCategories)
  }

  if (filteredStudents.length > 0) {
    filtersKeys.push('students')
    updatedFilters.push(filteredStudents)
  }

  if (filteredDomains.length > 0) {
    filtersKeys.push('domains')
    updatedFilters.push(filteredDomains)
  }

  if (venueFilter?.id) {
    filtersKeys.push('venue')
    updatedFilters.push(`venue.id:${venueFilter.id}`)
  }

  if (uai) {
    if (!uai.includes('all')) {
      filtersKeys.push('uaiCode')
    }
    updatedFilters.push(
      uai.map(uaiCode => `offer.educationalInstitutionUAICode:${uaiCode}`)
    )
  }

  if (onlyInMySchool) {
    filtersKeys.push('mySchool')
    updatedFilters.push('offer.eventAddressType:school')
  }

  return {
    queryFilters: updatedFilters,
    filtersKeys: filtersKeys,
  }
}
