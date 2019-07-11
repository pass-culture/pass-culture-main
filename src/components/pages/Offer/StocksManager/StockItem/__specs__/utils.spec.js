import moment from 'moment'
import 'moment/locale/fr'
import 'moment-timezone'

import {
  getDatetimeOneDayAfter,
  getDatetimeOneHourAfter,
  getDatetimeAtSpecificHoursAndMinutes,
  getRemainingStocksCount,
  formatPrice
} from '../utils'

describe('src | components | pages | Offer | StockItem | utils', () => {
  const bookings = [
    {
      amount: 45.0,
      dateCreated: '2019-02-12T09:18:36.077688Z',
      id: 'GGXQ',
      isCancelled: false,
      isUsed: false,
      modelName: 'Booking',
      quantity: 1,
      recommendationId: 'AYYC8',
      stockId: 'D28A',
      token: '8UNYCQ',
      userId: 'C9SQ',
    },
    {
      amount: 45.0,
      dateCreated: '2019-02-12T08:57:05.704555Z',
      id: 'GGLA',
      isCancelled: true,
      isUsed: false,
      modelName: 'Booking',
      quantity: 1,
      recommendationId: 'AXJRA',
      stockId: 'D28A',
      token: '9A2Q5A',
      userId: 'CMSA',
    },
    {
      amount: 45.0,
      dateCreated: '2019-02-12T10:04:46.588684Z',
      id: 'GHYQ',
      isCancelled: true,
      isUsed: false,
      modelName: 'Booking',
      quantity: 1,
      recommendationId: 'A5WVU',
      stockId: 'D28A',
      token: 'LUG9HU',
      userId: 'FNAQ',
    },
    {
      amount: 45.0,
      dateCreated: '2019-02-12T10:05:50.273241Z',
      id: 'GH3A',
      isCancelled: true,
      isUsed: false,
      modelName: 'Booking',
      quantity: 1,
      recommendationId: 'A6FY4',
      stockId: 'D28A',
      token: 'NMSQUA',
      userId: 'D9EQ',
    },
    {
      amount: 45.0,
      dateCreated: '2019-02-12T09:54:39.619611Z',
      id: 'GH8Q',
      isCancelled: true,
      isUsed: false,
      modelName: 'Booking',
      quantity: 1,
      recommendationId: 'A5KQA',
      stockId: 'D28A',
      token: 'SE6QTE',
      userId: 'DLSQ',
    },
    {
      amount: 45.0,
      dateCreated: '2019-02-12T10:36:04.299338Z',
      id: 'G97A',
      isCancelled: true,
      isUsed: false,
      modelName: 'Booking',
      quantity: 1,
      recommendationId: 'A7EQ4',
      stockId: 'D28A',
      token: 'X43QAY',
      userId: 'FZAA',
    },
    {
      amount: 45.0,
      dateCreated: '2019-03-13T17:20:31.263977Z',
      id: 'J6XQ',
      isCancelled: true,
      isUsed: false,
      modelName: 'Booking',
      quantity: 1,
      recommendationId: 'L4988',
      stockId: 'D28A',
      token: 'YABY2Q',
      userId: 'ETDA',
    },
    {
      amount: 45.0,
      dateCreated: '2019-03-14T17:51:49.542994Z',
      id: 'KCZQ',
      isCancelled: false,
      isUsed: false,
      modelName: 'Booking',
      quantity: 1,
      recommendationId: 'M6WX2',
      stockId: 'D28A',
      token: '8EZEA9',
      userId: 'AHQA',
    },
    {
      amount: 45.0,
      dateCreated: '2019-03-16T11:41:13.733061Z',
      id: 'KHWA',
      isCancelled: true,
      isUsed: false,
      modelName: 'Booking',
      quantity: 1,
      recommendationId: 'M2959',
      stockId: 'D28A',
      token: '2UTYT4',
      userId: 'FSDA',
    },
  ]
  describe('when there is available stock', () => {
    it('should compute remaining stock', () => {
      // given
      const available = 56

      // when
      const result = getRemainingStocksCount(available, bookings)

      // then
      expect(result).toStrictEqual(54)
    })
  })

  describe('when stock is unlimited', () => {
    it('should compute remaining illimited stock', () => {
      // given
      const available = null
      const bookings = 12

      // when
      const result = getRemainingStocksCount(available, bookings)

      // then
      expect(result).toStrictEqual('Illimité')
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
      const nextDatetime = getDatetimeAtSpecificHoursAndMinutes(
        datetime,
        23,
        59
      )

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
        expect(result).toStrictEqual("1.1")
      })

      it('should return a not formatted value when value contain a dot', () => {
        // given
        const value = '1.1'
        const readOnly = false

        // when
        const result = formatPrice(readOnly)(value)

        // then
        expect(result).toStrictEqual("1.1")
      })
    })
  })
})
