import { getRemaingStock } from '../utils'

describe('src | components | pages | Offer | EventOccurrenceAndStockItem | utils', () => {
  describe('When there is available stock', () => {
    it('should compute remaining stock', () => {
      // given
      const availableStock = 56
      const bookings = [{}, {}, {}, {}]

      // when
      const result = getRemaingStock(availableStock, bookings)

      // then
      expect(result).toEqual(52)
    })
  })
  describe('When there is no more available stock', () => {
    it('should compute remaining stock', () => {
      // given
      const availableStock = 0
      const bookings = [{}, {}, {}, {}]

      // when
      const result = getRemaingStock(availableStock, bookings)

      // then
      expect(result).toEqual(-4)
    })
  })
  describe('When stock is illimited', () => {
    it('should compute remaining illimited stock', () => {
      // given
      const availableStock = null
      const bookings = 12

      // when
      const result = getRemaingStock(availableStock, bookings)

      // then
      expect(result).toEqual('Illimité')
    })
  })
})
