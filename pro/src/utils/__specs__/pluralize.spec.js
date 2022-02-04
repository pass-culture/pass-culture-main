import { pluralize } from '../pluralize'

describe('pluralize', () => {
  describe('standard words', () => {
    it('should pluralize word if many offers', () => {
      // given
      const wordToPluralize = 'offre'

      // when
      const pluralizedWord = pluralize(5, wordToPluralize)

      // then
      expect(pluralizedWord).toBe('5 offres')
    })

    it('should singularize word if 0 offer', () => {
      // given
      const wordToSingularize = 'offres'

      // when
      const singularizedWord = pluralize(0, wordToSingularize)

      // then
      expect(singularizedWord).toBe('0 offre')
    })

    it('should singularize word if 1 offer', () => {
      // given
      const wordToSingularize = 'offres'

      // when
      const singularizedWord = pluralize(1, wordToSingularize)

      // then
      expect(singularizedWord).toBe('1 offre')
    })
  })

  describe('words with "x" plural', () => {
    it('should pluralize word if many bijoux with required ending', () => {
      // given
      const wordToPluralize = 'bijou'

      // when
      const pluralizedWord = pluralize(5, wordToPluralize, 'x')

      // then
      expect(pluralizedWord).toBe('5 bijoux')
    })

    it('should singularize word if 0 offer', () => {
      // given
      const wordToSingularize = 'bijoux'

      // when
      const singularizedWord = pluralize(0, wordToSingularize)

      // then
      expect(singularizedWord).toBe('0 bijou')
    })

    it('should singularize word if 1 offer', () => {
      // given
      const wordToSingularize = 'bijoux'

      // when
      const singularizedWord = pluralize(1, wordToSingularize)

      // then
      expect(singularizedWord).toBe('1 bijou')
    })
  })
})
