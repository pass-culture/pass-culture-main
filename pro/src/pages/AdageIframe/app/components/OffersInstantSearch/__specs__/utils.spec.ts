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
      adageFiltersToFacetFilters({ domains, uai: ['all'], students })
    ).toStrictEqual({
      queryFilters: [
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.educationalInstitutionUAICode:all'],
      ],
      filtersKeys: ['students', 'domains'],
    })
  })

  it('should return other uai facet filter', () => {
    expect(
      adageFiltersToFacetFilters({ domains, uai: ['123456'], students })
    ).toStrictEqual({
      queryFilters: [
        ['offer.students:Collège - 4e'],
        ['offer.domains:1'],
        ['offer.educationalInstitutionUAICode:123456'],
      ],
      filtersKeys: ['students', 'domains', 'uaiCode'],
    })
  })

  it('should not return uai facet filter', () => {
    expect(adageFiltersToFacetFilters({ domains, students })).toStrictEqual({
      queryFilters: [['offer.students:Collège - 4e'], ['offer.domains:1']],
      filtersKeys: ['students', 'domains'],
    })
  })
})
