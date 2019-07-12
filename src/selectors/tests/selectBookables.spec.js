import moment from 'moment'
import 'moment-timezone'

import {
  addModifierString,
  humanizeBeginningDate,
  markAsCancelled,
  setTimezoneOnBeginningDatetime,
} from '../selectBookables'
import { stockWithDates, stockWithoutDates } from './data/selectBookables'

const format = 'dddd DD/MM/YYYY à HH:mm'

describe('src | selectors| selectBookables', () => {
  describe('addModifierString', () => {
    it('add property named __modifiers__ to array of objects', () => {
      let value = []
      let expected = []
      let result = addModifierString()(value)
      expect(result).toStrictEqual(expected)
      value = [{ prop: 'prop' }]
      expected = [{ __modifiers__: ['selectBookables'], prop: 'prop' }]
      result = addModifierString()(value)
      expect(result).toStrictEqual(expected)
    })
  })
  describe('humanizeBeginningDate', () => {
    it('transform a date to an human readable one', () => {
      const dateString = new Date().toISOString()
      const dateMoment = moment(dateString)
      const dateExpected = dateMoment.format(format)
      let value = []
      let expected = []
      let result = addModifierString()(value)
      expect(result).toStrictEqual(expected)
      value = [
        { beginningDatetime: '', prop: 'prop' },
        { prop: 'prop' },
        { beginningDatetime: dateMoment, prop: 'prop' },
        { beginningDatetime: dateString, prop: 'prop' },
        { beginningDatetime: 'this is no date', prop: 'prop' },
        { beginningDatetime: 42, prop: 'prop' },
      ]
      expected = [
        { beginningDatetime: '', prop: 'prop' },
        { prop: 'prop' },
        {
          beginningDatetime: dateMoment,
          humanBeginningDate: dateExpected,
          prop: 'prop',
        },
        {
          beginningDatetime: dateString,
          humanBeginningDate: dateExpected,
          prop: 'prop',
        },
        {
          beginningDatetime: 'this is no date',
          prop: 'prop',
        },
        {
          beginningDatetime: 42,
          prop: 'prop',
        },
      ]
      result = humanizeBeginningDate()(value)
      expect(result).toStrictEqual(expected)
    })
  })
  describe('setTimezoneOnBeginningDatetime', () => {
    it('does nothing if stock as no beginning', () => {
      // given
      const timezone = 'Europe/Paris'
      const items = [stockWithoutDates]

      // when
      const results = setTimezoneOnBeginningDatetime(timezone)(items)

      // then
      expect(results[0].offerId).toBe('ATRQ')
      expect(results[0].beginningDatetime).toBeNull()
      expect(results[0].endDatetime).toBeNull()
    })
    it('sets timezones to beginningDatetime', () => {
      // given
      const timezone = 'Europe/Paris'
      const items = [stockWithDates]

      // when
      const results = setTimezoneOnBeginningDatetime(timezone)(items)

      // then
      expect(results[0].offerId).toBe('BYAQ')
      expect(results[0].beginningDatetime.format()).toBe('2019-04-19T20:30:00+02:00')
      expect(results[0].endDatetime).toBe('2019-04-20T20:00:00Z')
    })
  })
  describe('markAsCancelled', () => {
    it('should return userHasCancelledThisDate as true when the booking has been cancelled', () => {
      // given
      const bookings = [
        {
          id: 'HQ',
          isCancelled: true,
          modelName: 'Booking',
          recommendation: {},
          stock: {
            id: 'DU',
            modelName: 'Stock',
            offerId: 'CQ',
          },
        },
        {
          id: 'HY',
          isCancelled: false,
          modelName: 'Booking',
          recommendation: {},
          stock: {
            id: 'DQ',
            modelName: 'Stock',
            offerId: 'CQ',
          },
        },
      ]

      const items = [
        {
          id: 'DU',
          modelName: 'Stock',
          offerId: 'CQ',
          price: 23,
          userHasAlreadyBookedThisDate: true,
        },
      ]

      // when
      const results = markAsCancelled(bookings)(items)

      // then
      expect(results[0].userHasAlreadyBookedThisDate).toBe(true)
    })
  })
})
