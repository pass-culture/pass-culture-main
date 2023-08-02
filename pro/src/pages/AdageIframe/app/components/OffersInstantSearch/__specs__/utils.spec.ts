import { adageFiltersToFacetFilters } from '../utils'

describe('adageFiltersToFacetFilters', () => {
  const domains: string[] = ['1']
  const students: string[] = ['Collège - 4e']
  const departments: string[] = ['01']
  const academies: string[] = ['Paris']

  const categories: string[][] = [['categorie1', 'categorie2']]

  it('should return facet filter from form values', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        uai: ['all'],
        students,
        eventAddressType: 'school',
        departments,
        academies,
        categories,
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.schoolInterventionArea:01'],
        ['venue.academy:Paris'],
        ['offer.subcategoryId:categorie1', 'offer.subcategoryId:categorie2'],
        ['offer.educationalInstitutionUAICode:all'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'categories',
      ],
    })
  })

  it('should return other uai facet filter', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,

        uai: ['123456'],

        students,
        eventAddressType: 'school',

        departments,
        academies,
        categories,
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.schoolInterventionArea:01'],
        ['venue.academy:Paris'],
        ['offer.subcategoryId:categorie1', 'offer.subcategoryId:categorie2'],
        ['offer.educationalInstitutionUAICode:123456'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'categories',
        'uaiCode',
      ],
    })
  })

  it('should not return uai facet filter', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        students,
        eventAddressType: 'school',
        departments,
        academies,
        categories,
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.schoolInterventionArea:01'],
        ['venue.academy:Paris'],
        ['offer.subcategoryId:categorie1', 'offer.subcategoryId:categorie2'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'categories',
      ],
    })
  })

  it('should return offererVenue event type facet filter', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        students,
        eventAddressType: 'offererVenue',
        departments,
        academies,
        categories,
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:offererVenue', 'offer.eventAddressType:other'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['venue.departmentCode:01', 'offer.interventionArea:01'],
        ['venue.academy:Paris'],
        ['offer.subcategoryId:categorie1', 'offer.subcategoryId:categorie2'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'categories',
      ],
    })
  })
})
