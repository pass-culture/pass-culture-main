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
          { price: 0, isBookable: true },
          { price: 15.99, isBookable: true },
          { price: 100, isBookable: true },
          { price: 22.5, isBookable: false },
          { price: 0, isBookable: false },
          { price: 0, isBookable: true },
          { price: 56, isBookable: true },
        ]

        // When
        const result = getPriceRangeFromStocks(stocks)

        // Then
        expect(result).toStrictEqual([0, 100])
      })
    })
  })

  describe('when stocks contains price 0 and is bookable', () => {
    it('should return an array with the price', () => {
      // given
      const stocks = [
        {
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

  describe('when stocks contains price 0 and is not bookable', () => {
    it('should return an array with the price', () => {
      // given
      const stocks = [
        {
          price: 0,
          isBookable: false,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)

      // then
      expect(result).toStrictEqual([])
    })
  })

  describe('when stocks contains prices with decimals and not bookable stocks', () => {
    it('should not return the price of the offer without stock', () => {
      // given
      const stocks = [
        {
          price: 1.33,
          isBookable: true,
        },
        {
          price: 6.78,
          isBookable: false,
        },
      ]

      // when
      const result = getPriceRangeFromStocks(stocks)

      // then
      expect(result).toStrictEqual([1.33])
    })
  })
})
