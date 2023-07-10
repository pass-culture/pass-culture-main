import { Option } from 'pages/AdageIframe/app/types'

import { adageFiltersToFacetFilters } from '../utils'

describe('adageFiltersToFacetFilters', () => {
  const domains: Option<string>[] = [
    {
      label: 'Domaine 1',
      value: '1',
    },
  ]

  it('should return facet filter from form values', () => {
    expect(adageFiltersToFacetFilters({ domains, uai: ['all'] })).toStrictEqual(
      {
        queryFilters: [
          ['offer.domains:1'],
          ['offer.educationalInstitutionUAICode:all'],
        ],
        filtersKeys: ['domains'],
      }
    )
  })

  it('should return other uai facet filter', () => {
    expect(
      adageFiltersToFacetFilters({ domains, uai: ['123456'] })
    ).toStrictEqual({
      queryFilters: [
        ['offer.domains:1'],
        ['offer.educationalInstitutionUAICode:123456'],
      ],
      filtersKeys: ['domains', 'uaiCode'],
    })
  })

  it('should not return uai facet filter', () => {
    expect(adageFiltersToFacetFilters({ domains })).toStrictEqual({
      queryFilters: [['offer.domains:1']],
      filtersKeys: ['domains'],
    })
  })
})
