import { EacFormat } from 'apiClient/adage'

import { SearchFormValues } from '../OffersSearch/OffersSearch'
import { adageFiltersToFacetFilters, serializeFiltersForData } from '../utils'

describe('adageFiltersToFacetFilters', () => {
  const domains: string[] = ['1']
  const students: string[] = ['Collège - 4e']
  const departments: string[] = ['01']
  const academies: string[] = ['Paris']

  const categories: string[][] = [['categorie1', 'categorie2']]
  const formats: string[] = [EacFormat.CONCERT]

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
        formats,
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.schoolInterventionArea:01'],
        ['venue.academy:Paris'],
        ['offer.subcategoryId:categorie1', 'offer.subcategoryId:categorie2'],
        ['formats:Concert'],
        ['offer.educationalInstitutionUAICode:all'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'categories',
        'formats',
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
        formats,
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.schoolInterventionArea:01'],
        ['venue.academy:Paris'],
        ['offer.subcategoryId:categorie1', 'offer.subcategoryId:categorie2'],
        ['formats:Concert'],
        ['offer.educationalInstitutionUAICode:123456'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'categories',
        'formats',
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
        formats,
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.schoolInterventionArea:01'],
        ['venue.academy:Paris'],
        ['offer.subcategoryId:categorie1', 'offer.subcategoryId:categorie2'],
        ['formats:Concert'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'categories',
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
        departments,
        academies,
        categories,
        formats,
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:offererVenue', 'offer.eventAddressType:other'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['venue.departmentCode:01', 'offer.interventionArea:01'],
        ['venue.academy:Paris'],
        ['offer.subcategoryId:categorie1', 'offer.subcategoryId:categorie2'],
        ['formats:Concert'],
      ],
      filtersKeys: [
        'eventAddressType',
        'students',
        'domains',
        'departments',
        'academies',
        'categories',
        'formats',
      ],
    })
  })
})

describe('serializeFiltersForData', () => {
  const domainsOptions = [{ value: 1, label: 'domaine1' }]
  const categoriesOptions = [
    { label: 'Category 1', value: ['subcat1', 'subcat2'] },
    { label: 'Category 2', value: ['subcat2', 'subcat3'] },
  ]
  it('should return serialized filters', () => {
    const filters: SearchFormValues = {
      domains: ['1'],
      students: ['Collège - 4e'],
      eventAddressType: 'school',
      departments: ['01'],
      academies: ['Paris'],
      categories: [['subcat1', 'subcat3']],
      formats: [EacFormat.CONCERT],
      geolocRadius: 10,
    }
    const result = serializeFiltersForData(
      filters,
      'test',
      categoriesOptions,
      domainsOptions,
      true
    )

    expect(result).toStrictEqual({
      domains: ['domaine1'],
      query: 'test',
      students: ['Collège quatrième'],
      eventAddressType: 'school',
      departments: ['01'],
      academies: ['Paris'],
      categories: ['Category 1', 'Category 2'],
      formats: ['Concert'],
      geolocRadius: 10,
    })
  })
  it('should not serialize serialise formats if ff is not active', () => {
    const filters: SearchFormValues = {
      domains: ['1'],
      students: ['Collège - 4e'],
      eventAddressType: 'school',
      departments: ['01'],
      academies: ['Paris'],
      categories: [['subcat1', 'subcat3']],
      formats: [EacFormat.CONCERT],
      geolocRadius: 10,
    }
    const result = serializeFiltersForData(
      filters,
      'test',
      categoriesOptions,
      domainsOptions,
      false
    )

    expect(result).toStrictEqual({
      domains: ['domaine1'],
      query: 'test',
      students: ['Collège quatrième'],
      eventAddressType: 'school',
      departments: ['01'],
      academies: ['Paris'],
      categories: ['Category 1', 'Category 2'],
      formats: undefined,
      geolocRadius: 10,
    })
  })
})
