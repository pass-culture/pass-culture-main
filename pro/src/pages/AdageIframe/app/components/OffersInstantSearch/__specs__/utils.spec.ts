import { Option } from 'pages/AdageIframe/app/types'

import { adageFiltersToFacetFilters } from '../utils'

describe('adageFiltersToFacetFilters', () => {
  const domains: Option<string>[] = [
    {
      label: 'Domaine 1',
      value: '1',
    },
  ]

  const students: Option<string>[] = [
    { label: 'Collège - 4e', value: 'Collège - 4e' },
  ]

  it('should return facet filter from form values', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        uai: ['all'],
        students,
        eventAddressType: 'school',
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.educationalInstitutionUAICode:all'],
      ],
      filtersKeys: ['eventAddressType', 'students', 'domains'],
    })
  })

  it('should return other uai facet filter', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        uai: ['123456'],
        students,
        eventAddressType: 'school',
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.educationalInstitutionUAICode:123456'],
      ],
      filtersKeys: ['eventAddressType', 'students', 'domains', 'uaiCode'],
    })
  })

  it('should not return uai facet filter', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        students,
        eventAddressType: 'school',
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:school'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
      ],
      filtersKeys: ['eventAddressType', 'students', 'domains'],
    })
  })

  it('should return offererVenue event type facet filter', () => {
    expect(
      adageFiltersToFacetFilters({
        domains,
        students,
        eventAddressType: 'offererVenue',
      })
    ).toStrictEqual({
      queryFilters: [
        ['offer.eventAddressType:offererVenue', 'offer.eventAddressType:other'],
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
      ],
      filtersKeys: ['eventAddressType', 'students', 'domains'],
    })
  })
})
