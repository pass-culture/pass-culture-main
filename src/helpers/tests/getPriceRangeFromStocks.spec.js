import getPriceRangeFromStocks from '../getPriceRangeFromStocks'

describe('src | helpers | getPriceRangeFromStocks', () => {
  describe('when stock is not in good format', () => {
    it('returns an empty array', () => {
      const expected = []
      let stocks = []
      let result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual(expected)
      stocks = null
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual(expected)
      stocks = undefined
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual(expected)
      stocks = 1234
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual(expected)
      stocks = 'a string'
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual(expected)
      stocks = false
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual(expected)
      stocks = {}
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual(expected)
    })
    describe('when stocks exists', () => {
      it('returns an array of prices', () => {
        const stocks = [
          {},
          { available: 1, price: 0 },
          { available: 60, price: 15.99 },
          { available: 10, price: 100 },
          { available: 0, price: 22.5 },
          { available: 0, price: 0 },
          { available: null, price: 56 },
        ]
        const expected = [0, 15.99, 100, 56]
        const result = getPriceRangeFromStocks(stocks)
        expect(result).toStrictEqual(expected)
      })
    })
  })
  describe('when stocks contains no price', () => {
    it('should not', () => {
      const stocks = [{}, { available: null }, { available: 0 }]
      const result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual([])
    })
  })
  describe('when stocks contains price O and unlimited stock or no stock ', () => {
    it('should return an array with the price', () => {
      // given
      const stocks = [
        {
          available: 15,
          price: 0,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)
      const expected = [0]

      // then
      expect(result).toStrictEqual(expected)
    })
  })
  describe('when stocks contains price O and unlimited stock', () => {
    it('should return an array with the price', () => {
      // given
      const stocks = [
        {
          available: null,
          price: 0,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)
      const expected = [0]

      // then
      expect(result).toStrictEqual(expected)
    })
  })
  describe('when stocks contains price O and no stock ', () => {
    it('should return an array with the price', () => {
      // given
      const stocks = [
        {
          available: 0,
          price: 0,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)
      const expected = []

      // then
      expect(result).toStrictEqual(expected)
    })
  })
  describe('when stocks contains prices with decimals and no stock ', () => {
    it('should not return the price of the offer without stock', () => {
      // given
      const stocks = [
        {
          available: 67,
          price: 1.33,
        },
        {
          available: 0,
          price: 6.78,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)
      const expected = [1.33]

      // then
      expect(result).toStrictEqual(expected)
    })
  })
})
