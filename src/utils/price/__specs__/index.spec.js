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
      expect(result).toStrictEqual('A partir de 1 €')
    })

    it('should return price range starting from minimum price when minimum and maximum prices are different', () => {
      // when
      const result = formatResultPrice(1, 2, true)

      // then
      expect(result).toStrictEqual('A partir de 1 €')
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
      expect(result).toStrictEqual('A partir de 1 €')
    })
  })
})
