import { EacFormat } from 'apiClient/adage'

import { SearchFormValues } from '../OffersInstantSearch'
import { adageFiltersToFacetFilters, serializeFiltersForData } from '../utils'

const venueFilter = {
  id: 123,
  name: 'test',
  departementCode: '01',
  relative: [456],
}

describe('adageFiltersToFacetFilters', () => {
  const domains = [1]
  const students: string[] = ['Collège - 4e']
  const departments: string[] = ['01']
  const academies: string[] = ['Paris']
  const formats: string[] = [EacFormat.CONCERT]

  it('should return facet filter from form values', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        students,
        eventAddressType: 'school',
        locationType: 'SCHOOL',
        departments,
        academies,
        formats,
        venue: venueFilter,
      }, false)
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.schoolInterventionArea:01'],
        ['venue.academy:Paris'],
        ['formats:Concert'],
        ['venue.id:123', 'venue.id:456'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'formats',
        'venue',
      ],
    })
  })

  it('should return other uai facet filter', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        students,
        eventAddressType: 'school',
        locationType: 'SCHOOL',
        departments,
        academies,
        formats,
        venue: null,
      }, false)
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.schoolInterventionArea:01'],
        ['venue.academy:Paris'],
        ['formats:Concert'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'formats',
      ],
    })
  })

  it('should not return uai facet filter', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        students,
        eventAddressType: 'school',
        locationType: 'SCHOOL',
        departments,
        academies,
        formats,
        venue: null,
      }, false)
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.schoolInterventionArea:01'],
        ['venue.academy:Paris'],
        ['formats:Concert'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'formats',
      ],
    })
  })

  it('should return offererVenue event type facet filter', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        students,
        eventAddressType: 'offererVenue',
        locationType: 'SCHOOL',
        departments,
        academies,
        formats,
        venue: null,
      }, false)
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:offererVenue', 'offer.eventAddressType:other'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['venue.departmentCode:01', 'offer.interventionArea:01'],
        ['venue.academy:Paris'],
        ['formats:Concert'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'formats',
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
      eventAddressType: 'school',
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
      eventAddressType: 'school',
      locationType: 'SCHOOL',
      departments: ['01'],
      academies: ['Paris'],
      formats: ['Concert'],
      geolocRadius: 10,
      venue: undefined,
    })
  })
})
