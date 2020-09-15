import { pluralize } from '../pluralize'

describe('pluralize', () => {
  const wordToPluralize = 'offre'

  it('should not return number when word is given as first argument', () => {
    // when
    const pluralizedWord = pluralize(wordToPluralize, 3)

    // then
    expect(pluralizedWord).toEqual('offres')
  })

  it('should return string with plural if many offers', () => {
    // when
    const pluralizedWord = pluralize(5, wordToPluralize)

    // then
    expect(pluralizedWord).toEqual('5 offres')
  })

  it('should return string with singular if 0 offer', () => {
    // given
    const wordToSingularize = 'offres'

    // when
    const singularizedWord = pluralize(0, wordToSingularize)

    // then
    expect(singularizedWord).toEqual('0 offre')
  })

  it('should return string with singular if 1 offer', () => {
    // given
    const wordToSingularize = 'offres'

    // when
    const singularizedWord = pluralize(1, wordToSingularize)

    // then
    expect(singularizedWord).toEqual('1 offre')
  })
})
