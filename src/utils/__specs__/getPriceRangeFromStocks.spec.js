import getPriceRangeFromStocks from '../getPriceRangeFromStocks'

describe('src | helpers | getPriceRangeFromStocks', () => {
  describe('when stock is not in good format', () => {
    it('returns an empty array', () => {
      let stocks = []
      let result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual([])
      stocks = null
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual([])
      stocks = undefined
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual([])
      stocks = 1234
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual([])
      stocks = 'a string'
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual([])
      stocks = false
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual([])
      stocks = {}
      result = getPriceRangeFromStocks(stocks)
      expect(result).toStrictEqual([])
    })

    describe('when stocks exists', () => {
      it('returns only minimum and maximum prices', () => {
        // Given
        const stocks = [
          {},
          { available: 1, price: 0, isBookable: true },
          { available: 60, price: 15.99, isBookable: true },
          { available: 10, price: 100, isBookable: true },
          { available: 0, price: 22.5, isBookable: true },
          { available: 0, price: 0, isBookable: true },
          { available: 10, price: 0, isBookable: true },
          { available: null, price: 56, isBookable: true },
        ]

        // When
        const result = getPriceRangeFromStocks(stocks)

        // Then
        expect(result).toStrictEqual([0, 100])
      })
    })
  })

  describe('when stocks contains price 0 and unlimited stock or no stock', () => {
    it('should return an array with the price', () => {
      // given
      const stocks = [
        {
          available: 15,
          price: 0,
          isBookable: true,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)

      // then
      expect(result).toStrictEqual([0])
    })
  })

  describe('when stocks contains price 0 and unlimited stock', () => {
    it('should return an array with the price', () => {
      // given
      const stocks = [
        {
          available: null,
          price: 0,
          isBookable: true,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)
      // then
      expect(result).toStrictEqual([0])
    })
  })

  describe('when stocks contains price 0 and no stock', () => {
    it('should return an array with the price', () => {
      // given
      const stocks = [
        {
          available: 0,
          price: 0,
          isBookable: true,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)

      // then
      expect(result).toStrictEqual([])
    })
  })

  describe('when stocks contains prices with decimals and no stock', () => {
    it('should not return the price of the offer without stock', () => {
      // given
      const stocks = [
        {
          available: 67,
          price: 1.33,
          isBookable: true,
        },
        {
          available: 0,
          price: 6.78,
          isBookable: true,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)

      // then
      expect(result).toStrictEqual([1.33])
    })
  })

  describe('when stock is not bookable', () => {
    it('should not include that stock in the range', () => {
      // given
      const stocks = [
        {
          available: 10,
          price: 1.33,
          isBookable: true,
        },
        {
          available: 10,
          price: 4.31,
          isBookable: true,
        },
        {
          available: 10,
          price: 6.78,
          isBookable: true,
        },
        {
          available: 10,
          price: 8.52,
          isBookable: false,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)

      // then
      expect(result).toStrictEqual([1.33, 6.78])
    })
  })
})
