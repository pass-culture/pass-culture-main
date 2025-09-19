import { CollectiveLocationType, type VenueResponse } from '@/apiClient/adage'
import type { Facets, Option } from '@/pages/AdageIframe/app/types'

import type { SearchFormValues } from './OffersInstantSearch'
import { studentsForData } from './OffersSearch/OfferFilters/studentsOptions'

export const ADAGE_FILTERS_DEFAULT_VALUES: SearchFormValues = {
  domains: [],
  students: [],
  departments: [],
  academies: [],
  locationType: CollectiveLocationType.TO_BE_DEFINED,
  geolocRadius: 50,
  formats: [],
  venue: null,
}

export const adageFiltersToFacetFilters = ({
  domains,
  students,
  locationType,
  departments,
  academies,
  formats,
  venue,
}: {
  domains: number[]
  students: string[]
  departments: string[]
  academies: string[]
  locationType: string
  formats: string[]
  venue: VenueResponse | null
}) => {
  const updatedFilters: Facets = []
  const filtersKeys: string[] = []

  const filteredDomains: string[] = domains.map(
    (domain) => `offer.domains:${domain}`
  )

  const filteredStudents: string[] = students.map(
    (student) => `offer.students:${student}`
  )

  const filteredFormats: string[] = formats.map((format) => `formats:${format}`)

  const filteredDepartments: string[] = departments.flatMap((department) => [
    `offer.interventionArea:${department}`,
    `venue.departmentCode:${department}`,
  ])

  const filteredAcademies: string[] = academies.map(
    (academy) => `venue.academy:${academy}`
  )

  filtersKeys.push('locationType')
  if (locationType === CollectiveLocationType.SCHOOL) {
    updatedFilters.push(['offer.locationType:SCHOOL'])
  }

  if (locationType === CollectiveLocationType.ADDRESS) {
    updatedFilters.push([
      'offer.locationType:ADDRESS',
      'offer.locationType:TO_BE_DEFINED',
    ])
  }

  const filteredVenues = venue
    ? [
        `venue.id:${venue.id}`,
        ...venue.relative.map((venueId) => `venue.id:${venueId}`),
      ]
    : []

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

  if (filteredFormats.length > 0) {
    filtersKeys.push('formats')
    updatedFilters.push(filteredFormats)
  }

  if (filteredVenues.length > 0) {
    filtersKeys.push('venue')
    updatedFilters.push(filteredVenues)
  }

  return {
    queryFilters: updatedFilters,
    filtersKeys,
  }
}

export const serializeFiltersForData = (
  filters: SearchFormValues,
  currentSearch: string | null,
  domainsOptions: Option<number>[]
) => {
  return {
    ...filters,
    query: currentSearch,
    domains: filters.domains.map(
      (domainId) =>
        domainsOptions.find((option) => option.value === Number(domainId))
          ?.label
    ),
    students: filters.students.map(
      (student) =>
        studentsForData.find((s) => s.label === student)?.valueForData
    ),
    formats: filters.formats,
    venue: filters.venue
      ? [filters.venue.id, ...filters.venue.relative.map((venueId) => venueId)]
      : undefined,
  }
}

export const areFiltersEmpty = (filters: SearchFormValues) => {
  return (
    // Primitives defaults
    filters.locationType === CollectiveLocationType.TO_BE_DEFINED &&
    filters.geolocRadius === 50 &&
    // Array defaults (empty)
    filters.domains.length === 0 &&
    filters.departments.length === 0 &&
    filters.academies.length === 0 &&
    filters.formats.length === 0 &&
    filters.students.length === 0 &&
    // venue default is null
    filters.venue === null
  )
}
