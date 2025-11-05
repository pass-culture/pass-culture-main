import { pluralizeFr } from '../pluralize'

describe('pluralize french', () => {
  it.each([
    { count: 0, expected: 'offre' },
    { count: 1, expected: 'offre' },
    { count: 2, expected: 'offres' },
    { count: 50, expected: 'offres' },
  ])('should pluralize correctly for $count item(s)', ({ count, expected }) => {
    const pluralizedWord = pluralizeFr(count, 'offre', 'offres')
    expect(pluralizedWord).toBe(expected)
  })
})
