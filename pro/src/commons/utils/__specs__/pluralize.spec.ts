import { pluralize } from '../pluralize'

describe('pluralize', () => {
  describe('standard words', () => {
    it('should pluralize word if many offers', () => {
      const wordToPluralize = 'offre'

      const pluralizedWord = pluralize(5, wordToPluralize)

      expect(pluralizedWord).toBe('5 offres')
    })

    it('should singularize word if 0 offer', () => {
      const wordToSingularize = 'offres'

      const singularizedWord = pluralize(0, wordToSingularize)

      expect(singularizedWord).toBe('0 offre')
    })

    it('should singularize word if 1 offer', () => {
      const wordToSingularize = 'offres'

      const singularizedWord = pluralize(1, wordToSingularize)

      expect(singularizedWord).toBe('1 offre')
    })
  })

  describe('words with "x" plural', () => {
    it('should pluralize word if many bijoux with required ending', () => {
      const wordToPluralize = 'bijou'

      const pluralizedWord = pluralize(5, wordToPluralize, 'x')

      expect(pluralizedWord).toBe('5 bijoux')
    })

    it('should singularize word if 0 offer', () => {
      const wordToSingularize = 'bijoux'

      const singularizedWord = pluralize(0, wordToSingularize)

      expect(singularizedWord).toBe('0 bijou')
    })

    it('should singularize word if 1 offer', () => {
      const wordToSingularize = 'bijoux'

      const singularizedWord = pluralize(1, wordToSingularize)

      expect(singularizedWord).toBe('1 bijou')
    })
  })
})
