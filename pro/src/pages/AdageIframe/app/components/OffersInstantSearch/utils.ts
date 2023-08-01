import flatMap from 'lodash/flatMap'

import { VenueResponse } from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import { Facets, Option } from 'pages/AdageIframe/app/types'

import { SearchFormValues } from './OffersSearch/OffersSearch'

interface FacetsWithData {
  queryFilters: Facets
  filtersKeys: string[]
}

export const ADAGE_FILTERS_DEFAULT_VALUES: SearchFormValues = {
  query: '',
  domains: [],
  students: [],
  departments: [],
  academies: [],
  categories: [],
  eventAddressType: OfferAddressType.OTHER,
}

export const computeFiltersInitialValues = (
  userDepartmentCode?: string | null
) => {
  if (!userDepartmentCode) {
    return ADAGE_FILTERS_DEFAULT_VALUES
  }
  return {
    ...ADAGE_FILTERS_DEFAULT_VALUES,
    departments: [userDepartmentCode],
    eventAddressType: OfferAddressType.OTHER,
  }
}

export const computeVenueFacetFilter = (venueFilter: VenueResponse): string[] =>
  [venueFilter.id, ...venueFilter.relative].map(
    venueId => `venue.id:${venueId}`
  )

export const adageFiltersToFacetFilters = ({
  domains,
  uai,
  students,
  eventAddressType,
  departments,
  academies,
  categories,
}: {
  domains: string[]
  uai?: string[] | null
  students: string[]
  departments: string[]
  academies: string[]
  eventAddressType: string
  categories: string[][]
}) => {
  const updatedFilters: Facets = []
  const filtersKeys: string[] = []

  const filteredDomains: string[] = domains.map(
    domain => `offer.domains:${domain}`
  )

  const filteredStudents: string[] = students.map(
    student => `offer.students:${student}`
  )

  let filteredDepartments: string[] = []
  if (eventAddressType == OfferAddressType.SCHOOL) {
    filteredDepartments = departments.flatMap(department => [
      `offer.schoolInterventionArea:${department}`,
    ])
  } else {
    filteredDepartments = departments.flatMap(department => [
      `venue.departmentCode:${department}`,
      `offer.interventionArea:${department}`,
    ])
  }

  const filteredAcademies: string[] = academies.map(
    academy => `venue.academy:${academy}`
  )

  switch (eventAddressType) {
    case 'school':
      filtersKeys.push('eventAddressType')
      updatedFilters.push([`offer.eventAddressType:school`])
      break
    case 'offererVenue':
      filtersKeys.push('eventAddressType')
      updatedFilters.push([
        `offer.eventAddressType:offererVenue`,
        `offer.eventAddressType:other`,
      ])
      break
    default:
      break
  }

  const filteredCategories: string[] = categories.flatMap(categoryValue =>
    categoryValue.map(subcategoryId => `offer.subcategoryId:${subcategoryId}`)
  )

  if (filteredStudents.length > 0) {
    filtersKeys.push('students')
    updatedFilters.push(filteredStudents)
  }

  if (filteredDomains.length > 0) {
    filtersKeys.push('domains')
    updatedFilters.push(filteredDomains)
  }

  if (filteredDepartments.length > 0) {
    filtersKeys.push('departments')
    updatedFilters.push(filteredDepartments)
  }

  if (filteredAcademies.length > 0) {
    filtersKeys.push('academies')
    updatedFilters.push(filteredAcademies)
  }

  if (filteredCategories.length > 0) {
    filtersKeys.push('categories')
    updatedFilters.push(filteredCategories)
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
