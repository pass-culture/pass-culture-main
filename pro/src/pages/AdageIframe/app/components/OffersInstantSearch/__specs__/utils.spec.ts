import { EacFormat } from '@/apiClient/adage'

import type { SearchFormValues } from '../OffersInstantSearch'
import { adageFiltersToFacetFilters, serializeFiltersForData } from '../utils'

const venueFilter = {
  id: 123,
  name: 'Venue Name',
  publicName: 'Venue Public Name',
  departementCode: '01',
  relative: [456],
}

describe('adageFiltersToFacetFilters', () => {
  const domains = [1]
  const students: string[] = ['Collège - 4e']
  const departments: string[] = ['01']
  const academies: string[] = ['Paris']
  const formats: string[] = [EacFormat.CONCERT]

  it('should return locationType SCHOOL in facet filter when location is SCHOOL', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        students,
        locationType: 'SCHOOL',
        departments,
        academies,
        formats,
        venue: venueFilter,
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.locationType:SCHOOL'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.interventionArea:01', 'venue.departmentCode:01'],
        ['venue.academy:Paris'],
        ['formats:Concert'],
        ['venue.id:123', 'venue.id:456'],
      ],
      filtersKeys: [
        'locationType',
        'students',
        'domains',
        'departments',
        'academies',
        'formats',
        'venue',
      ],
    })
  })

  it('should return locationType ADDRESS and TO_BE_DEFINED when value is ADDRESS in facet filter', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        students,
        locationType: 'ADDRESS',
        departments,
        academies,
        formats,
        venue: venueFilter,
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.locationType:ADDRESS', 'offer.locationType:TO_BE_DEFINED'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.interventionArea:01', 'venue.departmentCode:01'],
        ['venue.academy:Paris'],
        ['formats:Concert'],
        ['venue.id:123', 'venue.id:456'],
      ],
      filtersKeys: [
        'locationType',
        'students',
        'domains',
        'departments',
        'academies',
        'formats',
        'venue',
      ],
    })
  })
})

describe('serializeFiltersForData', () => {
  const domainsOptions = [{ value: 1, label: 'domaine1' }]

  it('should return serialized filters', () => {
    const filters: SearchFormValues = {
      domains: [1],
      students: ['Collège - 4e'],
      locationType: 'SCHOOL',
      departments: ['01'],
      academies: ['Paris'],
      formats: [EacFormat.CONCERT],
      geolocRadius: 10,
      venue: null,
    }
    const result = serializeFiltersForData(filters, 'test', domainsOptions)

    expect(result).toStrictEqual({
      domains: ['domaine1'],
      query: 'test',
      students: ['Collège quatrième'],
      locationType: 'SCHOOL',
      departments: ['01'],
      academies: ['Paris'],
      formats: ['Concert'],
      geolocRadius: 10,
      venue: undefined,
    })
  })
})
