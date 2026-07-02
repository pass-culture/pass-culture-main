import { CollectiveLocationType, EacFormat } from '@/apiClient/adage'

import type { SearchFormValues } from '../OffersInstantSearch'
import { adageFiltersToFacetFilters, serializeFiltersForData } from '../utils'

const venueFilter = {
  id: 123,
  name: 'Venue Name',
  publicName: 'Venue Public Name',
  departementCode: '01',
  relative: [456],
  adageId: '1',
}

describe('adageFiltersToFacetFilters', () => {
  const domains = [1]
  const students: string[] = ['Collège - 4e']
  const departments: string[] = ['01']
  const academies: string[] = ['Paris']
  const formats: string[] = [EacFormat.CONCERT]

  it('should return locationType SCHOOL in facet filter when location is SCHOOL', () => {
    const result = adageFiltersToFacetFilters({
      domains,
      students,
      locationType: CollectiveLocationType.SCHOOL,
      departments,
      academies,
      formats,
      venue: venueFilter,
    })

    expect(result.queryFilters).toStrictEqual([
      ['offer.locationType:SCHOOL'],
      ['offer.students:Collège - 4e'],
      ['offer.domains:1'],
      ['offer.departmentCodes:01'],
      ['offer.academies:Paris'],
      ['formats:Concert'],
      ['venue.id:123', 'venue.id:456'],
    ])
    expect(result.filtersKeys).toStrictEqual([
      'locationType',
      'students',
      'domains',
      'departments',
      'academies',
      'formats',
      'venue',
    ])
  })

  it('should return locationType ADDRESS and TO_BE_DEFINED when value is ADDRESS in facet filter', () => {
    const result = adageFiltersToFacetFilters({
      domains,
      students,
      locationType: CollectiveLocationType.ADDRESS,
      departments,
      academies,
      formats,
      venue: venueFilter,
    })

    expect(result.queryFilters).toStrictEqual([
      ['offer.locationType:ADDRESS', 'offer.locationType:TO_BE_DEFINED'],
      ['offer.students:Collège - 4e'],
      ['offer.domains:1'],
      ['offer.departmentCodes:01'],
      ['offer.academies:Paris'],
      ['formats:Concert'],
      ['venue.id:123', 'venue.id:456'],
    ])
  })

  describe('locations filter with institution department', () => {
    it('should generate locations filter without department when no departmentCode provided', () => {
      const result = adageFiltersToFacetFilters({
        domains: [],
        students: [],
        locationType: CollectiveLocationType.SCHOOL,
        departments: [],
        academies: [],
        formats: [],
        venue: null,
      })

      expect(result.locationsFilter).toBe(
        'offer.locationType:ADDRESS<score=3> OR offer.locationType:SCHOOL<score=2> OR offer.locationType:TO_BE_DEFINED<score=1>'
      )
    })

    it('should generate locations filter for SCHOOL with department when departmentCode provided', () => {
      const result = adageFiltersToFacetFilters({
        domains: [],
        students: [],
        locationType: CollectiveLocationType.SCHOOL,
        departments: [],
        academies: [],
        formats: [],
        venue: null,
        institutionDepartmentCode: '75',
      })

      expect(result.locationsFilter).toBe(
        '(offer.locationType:SCHOOL<score=2>) AND (offer.interventionArea:"75")'
      )
    })

    it('should generate locations filter for ADDRESS with department when departmentCode provided', () => {
      const result = adageFiltersToFacetFilters({
        domains: [],
        students: [],
        locationType: CollectiveLocationType.ADDRESS,
        departments: [],
        academies: [],
        formats: [],
        venue: null,
        institutionDepartmentCode: '75',
      })

      expect(result.locationsFilter).toBe(
        '(offer.locationType:ADDRESS<score=3> OR offer.locationType:TO_BE_DEFINED<score=1>) AND (offer.locationType:ADDRESS OR offer.interventionArea:"75")'
      )
    })

    it('should generate locations filter for TO_BE_DEFINED with department when departmentCode provided', () => {
      const result = adageFiltersToFacetFilters({
        domains: [],
        students: [],
        locationType: CollectiveLocationType.TO_BE_DEFINED,
        departments: [],
        academies: [],
        formats: [],
        venue: null,
        institutionDepartmentCode: '75',
      })

      expect(result.locationsFilter).toBe(
        '(offer.locationType:ADDRESS<score=3> OR offer.locationType:SCHOOL<score=2> OR offer.locationType:TO_BE_DEFINED<score=1>) AND (offer.locationType:ADDRESS OR offer.interventionArea:"75")'
      )
    })
  })
})

describe('serializeFiltersForData', () => {
  const domainsOptions = [{ value: 1, label: 'domaine1' }]

  it('should return serialized filters', () => {
    const filters: SearchFormValues = {
      domains: [1],
      students: ['Collège - 4e'],
      locationType: CollectiveLocationType.SCHOOL,
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
      locationType: CollectiveLocationType.SCHOOL,
      departments: ['01'],
      academies: ['Paris'],
      formats: ['Concert'],
      geolocRadius: 10,
      venue: undefined,
    })
  })
})
