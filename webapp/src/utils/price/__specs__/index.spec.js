import { formatResultPrice } from '../index'

describe('formatResultPrice', () => {
  describe('offer is duo', () => {
    it('should return gratuit when minimum price is 0', () => {
      // when
      const result = formatResultPrice(0, 1, true)

      // then
      expect(result).toStrictEqual('Gratuit')
    })

    it('should return price range starting from minimum price when minimum and maximum prices are similar', () => {
      // when
      const result = formatResultPrice(1, 1, true)

      // then
      expect(result).toStrictEqual('À partir de 1 €')
    })

    it('should return price range starting from minimum price when minimum and maximum prices are different', () => {
      // when
      const result = formatResultPrice(1, 2, true)

      // then
      expect(result).toStrictEqual('À partir de 1 €')
    })

    it('should return price range starting from minimum price when minimum and maximum prices are different and contain decimals', () => {
      // when
      const result = formatResultPrice(1.1, 2.7, true)

      // then
      expect(result).toStrictEqual('À partir de 1,10 €')
    })
  })

  describe('offer is not duo', () => {
    it('should return gratuit when minimum price is 0', () => {
      // when
      const result = formatResultPrice(0, 1, false)

      // then
      expect(result).toStrictEqual('Gratuit')
    })

    it('should return the minimum price when minimum and maximum prices are similar', () => {
      // when
      const result = formatResultPrice(1, 1, false)

      // then
      expect(result).toStrictEqual('1 €')
    })

    it('should return price range starting from minimum price when minimum and maximum prices are different', () => {
      // when
      const result = formatResultPrice(1, 2, false)

      // then
      expect(result).toStrictEqual('À partir de 1 €')
    })

    it('should return the minimum price when minimum and maximum prices are similar and contain decimals', () => {
      // when
      const result = formatResultPrice(1.6, 1.6, false)

      // then
      expect(result).toStrictEqual('1,60 €')
    })
  })
})
