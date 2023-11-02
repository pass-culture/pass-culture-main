import { getDefaultFacetFilterUAICodeValue } from 'utils/facetFilters'

describe('getDefaultFacetFilterUAICodeValue', () => {
  it('should return filters with uai if user has one', () => {
    const expectedFilters = [
      [
        'offer.educationalInstitutionUAICode:all',
        'offer.educationalInstitutionUAICode:ABC123',
      ],
    ]

    expect(getDefaultFacetFilterUAICodeValue('ABC123')).toEqual(expectedFilters)
  })
  it('should not return filters with departement if user has one', () => {
    const expectedFilters = [['offer.educationalInstitutionUAICode:all']]

    expect(getDefaultFacetFilterUAICodeValue(null)).toEqual(expectedFilters)
  })
  it('should return filters with venue filter if valued', () => {
    const venueFilter = {
      id: 1,
      name: 'test',
      relative: [2],
      departementCode: '30',
    }
    const expectedFilters = [
      ['venue.id:1', 'venue.id:2'],
      ['offer.educationalInstitutionUAICode:all'],
    ]

    expect(getDefaultFacetFilterUAICodeValue(null, venueFilter)).toEqual(
      expectedFilters
    )
  })
})
