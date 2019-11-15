import moment from 'moment'
import 'moment-timezone'
import {
  addModifierString,
  humanizeBeginningDate,
  markAsCancelled,
  selectIsNotBookableByRouterMatch,
  setTimezoneOnBeginningDatetime,
} from '../bookablesSelectors'

const format = 'dddd DD/MM/YYYY à HH:mm'

describe('selectBookables', () => {
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
      const stockWithoutDates = {
        available: 10,
        beginningDatetime: null,
        bookingLimitDatetime: null,
        endDatetime: null,
        id: 'C3LA',
        isSoftDeleted: false,
        modelName: 'Stock',
        offerId: 'ATRQ',
        price: 25.0,
      }
      const items = [stockWithoutDates]
      const timezone = 'Europe/Paris'

      // when
      const results = setTimezoneOnBeginningDatetime(timezone)(items)

      // then
      expect(results[0].offerId).toBe('ATRQ')
      expect(results[0].beginningDatetime).toBeNull()
      expect(results[0].endDatetime).toBeNull()
    })
    it('sets timezones to beginningDatetime', () => {
      // given
      const stockWithDate = {
        available: 10,
        beginningDatetime: '2019-04-19T18:30:00Z',
        bookingLimitDatetime: null,
        endDatetime: '2019-04-20T20:00:00Z',
        id: 'C3LA',
        isSoftDeleted: false,
        modelName: 'Stock',
        offerId: 'BYAQ',
        price: 25.0,
      }
      const items = [stockWithDate]
      const timezone = 'Europe/Paris'

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

describe('selectIsNotBookableByRouterMatch', () => {
  let offer

  beforeEach(() => {
    offer = {
      id: 'AE',
      isNotBookable: false,
    }
  })

  it('should return false when offerId in match', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [],
        offers: [offer],
        recommendations: [],
        stocks: [],
      },
    }
    const match = {
      params: {
        offerId: 'AE',
      },
    }

    // when
    const result = selectIsNotBookableByRouterMatch(state, match)

    // then
    expect(result).toBe(false)
  })

  it('should return false when bookingId in match resolves booking', () => {
    // given
    const bookingId = 'BF'
    const booking = {
      id: bookingId,
      stock: { offerId: 'AE' },
      stockId: 'AA',
    }
    const state = {
      data: {
        bookings: [booking],
        favorites: [],
        mediations: [],
        offers: [offer],
        recommendations: [],
        stocks: [{ id: 'AA' }],
      },
    }
    const match = {
      params: {
        bookingId,
      },
    }

    // when
    const result = selectIsNotBookableByRouterMatch(state, match)

    // then
    expect(result).toBe(false)
  })

  it('should return false when favoriteId in match resolves offer', () => {
    // given
    const favoriteId = 'BF'
    const favorite = { id: favoriteId, offerId: 'AE' }
    const state = {
      data: {
        bookings: [],
        favorites: [favorite],
        mediations: [],
        offers: [offer],
        recommendations: [],
        stocks: [],
      },
    }
    const match = {
      params: {
        favoriteId,
      },
    }

    // when
    const result = selectIsNotBookableByRouterMatch(state, match)

    // then
    expect(result).toBe(false)
  })
})

