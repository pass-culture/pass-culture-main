import flatMap from 'lodash/flatMap'

import { VenueResponse } from 'apiClient/adage'
import { Facets, Option } from 'pages/AdageIframe/app/types'

interface FacetsWithData {
  queryFilters: Facets
  filtersKeys: string[]
}

export const computeVenueFacetFilter = (
  venueFilter?: VenueResponse | null
): string[] =>
  venueFilter
    ? [venueFilter.id, ...venueFilter.relative].map(
        venueId => `venue.id:${venueId}`
      )
    : []

export const populateFacetFilters = ({
  departments,
  categories,
  students,
  domains,
  venueFilter = null,
  onlyInMySchool,
  onlyInMyDpt,
  uai,
}: {
  departments: Option[]
  categories: Option<string[]>[]
  students: Option[]
  domains: Option<number>[]
  venueFilter: VenueResponse | null
  onlyInMySchool: boolean
  onlyInMyDpt: boolean
  uai?: string[] | null
}): FacetsWithData => {
  const updatedFilters: Facets = []
  const filtersKeys: string[] = []

  let filteredDepartments: string[] = []
  if (onlyInMyDpt || onlyInMySchool) {
    filteredDepartments = departments.flatMap(department => [
      ...(onlyInMyDpt ? [`venue.departmentCode:${department.value}`] : []),
      ...(onlyInMySchool
        ? [`offer.schoolInterventionArea:${department.value}`]
        : []),
    ])
  } else {
    filteredDepartments = departments.flatMap(department => [
      `venue.departmentCode:${department.value}`,
      `offer.interventionArea:${department.value}`,
    ])
  }

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
    if (onlyInMySchool) {
      filtersKeys.push('interventionArea')
      filtersKeys.push('mySchool')
    }

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
    updatedFilters.push(computeVenueFacetFilter(venueFilter))
  }

  if (uai) {
    if (!uai.includes('all')) {
      filtersKeys.push('uaiCode')
    }
    updatedFilters.push(
      uai.map(uaiCode => `offer.educationalInstitutionUAICode:${uaiCode}`)
    )
  }

  return {
    queryFilters: updatedFilters,
    filtersKeys: filtersKeys,
  }
}
