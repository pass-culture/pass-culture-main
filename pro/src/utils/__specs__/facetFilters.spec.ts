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
  it('should return filters with departement if user has one', () => {
    const expectedFilters = [
      [`venue.departmentCode:75`, `offer.interventionArea:75`],
      ['offer.educationalInstitutionUAICode:all'],
    ]

    expect(getDefaultFacetFilterUAICodeValue(null, '75')).toEqual(
      expectedFilters
    )
  })
  it('should return filters with venue filter if valued', () => {
    const venueFilter = {
      id: 1,
      name: 'test',
      relative: [],
      departementCode: '30',
    }
    const expectedFilters = [
      [
        `venue.departmentCode:75`,
        `offer.interventionArea:75`,
        `venue.departmentCode:30`,
        `offer.interventionArea:30`,
      ],
      ['offer.educationalInstitutionUAICode:all'],
    ]

    expect(getDefaultFacetFilterUAICodeValue(null, '75', venueFilter)).toEqual(
      expectedFilters
    )
  })
})
