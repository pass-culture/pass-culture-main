import moment from 'moment'
import 'moment/locale/fr'
import 'moment-timezone'

import {
  getDatetimeOneDayAfter,
  getDatetimeOneHourAfter,
  getDatetimeAtSpecificHoursAndMinutes,
  getRemainingStocksCount,
  formatPrice,
} from '../utils'

describe('src | components | pages | Offer | StockItem | utils', () => {
  describe('getRemainingStocksCount', () => {
    it('should return `Illimité` when available stock equal to 0', () => {
      // given
      const available = 0
      const remainingQuantity = 1

      // when
      const result = getRemainingStocksCount(available, remainingQuantity)

      // then
      expect(result).toBe('Illimité')
    })

    it('should return remainingQuantity when available stock is greater than 0', () => {
      // given
      const available = 1
      const remainingQuantity = 4

      // when
      const result = getRemainingStocksCount(available, remainingQuantity)

      // then
      expect(result).toBe(4)
    })
  })

  describe('getDatetimeOneDayAfter', () => {
    it('should getDatetimeOneDayAfter', () => {
      // given
      const datetime = '2019-04-27T19:00:00Z'

      // when
      const nextDatetime = getDatetimeOneDayAfter(datetime)

      // then
      expect(nextDatetime).toStrictEqual('2019-04-28T19:00:00.000Z')
    })
    it('should getDatetimeOneHourAfter', () => {
      // given
      const datetime = '2019-04-27T19:00:00Z'

      // when
      const nextDatetime = getDatetimeOneHourAfter(datetime)

      // then
      expect(nextDatetime).toStrictEqual('2019-04-27T20:00:00.000Z')
    })
    it('should getDatetimeAtSpecificHoursAndMinutes', () => {
      // given
      const datetime = moment('2019-04-27T19:00:00Z').tz('Europe/Paris')

      // when
      const nextDatetime = getDatetimeAtSpecificHoursAndMinutes(datetime, 23, 59)

      // then
      expect(nextDatetime).toStrictEqual('2019-04-27T21:59:00.000Z')
    })
  })

  describe('formatPrice', () => {
    describe('gratuit label', () => {
      it('should return "Gratuit" label when isReadOnly is true and value is null', () => {
        // given
        const readOnly = true
        const value = null

        // when
        const result = formatPrice(readOnly)(value)

        // then
        expect(result).toBe('Gratuit')
      })

      it('should return "Gratuit" label when isReadOnly is true and value is equal to 0', () => {
        // given
        const readOnly = true
        const value = 0

        // when
        const result = formatPrice(readOnly)(value)

        // then
        expect(result).toBe('Gratuit')
      })

      it('should return "Gratuit" label when isReadOnly is true and value is empty', () => {
        // given
        const readOnly = true
        const value = ''

        // when
        const result = formatPrice(readOnly)(value)

        // then
        expect(result).toBe('Gratuit')
      })
    })

    describe('formatted price', () => {
      it('should replace comma sign to dot sign when value is a string and contains numbers', () => {
        // given
        const value = '1,1'
        const readOnly = false

        // when
        const result = formatPrice(readOnly)(value)

        // then
        expect(result).toStrictEqual('1.1')
      })

      it('should return a not formatted value when value contain a dot', () => {
        // given
        const value = '1.1'
        const readOnly = false

        // when
        const result = formatPrice(readOnly)(value)

        // then
        expect(result).toStrictEqual('1.1')
      })
    })
  })
})
