import { VenueResponse } from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import { Facets, Option } from 'pages/AdageIframe/app/types'
import { inferCategoryLabelsFromSubcategories } from 'utils/collectiveCategories'

import { SearchFormValues } from './OffersSearch/OffersSearch'

export const ADAGE_FILTERS_DEFAULT_VALUES: SearchFormValues = {
  domains: [],
  students: [],
  departments: [],
  academies: [],
  categories: [],
  eventAddressType: OfferAddressType.OTHER,
  geolocRadius: 50,
}

export const computeFiltersInitialValues = (
  userDepartmentCode?: string | null,
  venueFilter?: VenueResponse | null
) => {
  const venueDepartementFilter =
    venueFilter && venueFilter.departementCode !== userDepartmentCode
      ? [venueFilter.departementCode]
      : []
  return {
    ...ADAGE_FILTERS_DEFAULT_VALUES,
    departments: userDepartmentCode
      ? [userDepartmentCode, ...venueDepartementFilter]
      : ADAGE_FILTERS_DEFAULT_VALUES.departments,
  }
}

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

export const serializeFiltersForData = (
  filters: SearchFormValues,
  currentSearch: string | null,
  categoriesOptions: Option<string[]>[],
  domainsOptions: Option<number>[]
) => {
  return {
    ...filters,
    query: currentSearch,
    categories: inferCategoryLabelsFromSubcategories(
      filters.categories,
      categoriesOptions
    ),
    domains: filters.domains.map(
      domainId =>
        domainsOptions.find(option => option.value === Number(domainId))?.label
    ),
  }
}
