// jest --env=jsdom ./src/selectors/tests/selectBookings --watch
import moment from 'moment'
import get from 'lodash.get'

import AllBookingsDataset from './data/selectBookings'
import {
  filterValidBookings,
  filterBookingsInLessThanTwoDays,
  filterBookingsInMoreThanTwoDaysOrPast,
  selectBookingById,
} from '../selectBookings'

describe('src | selectors | selectBookings', () => {
  describe(' selectBookingById', () => {
    it('should return booking matching id', () => {
      // given
      const state = {
        data: {
          bookings: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
        },
      }
      // When
      const result = selectBookingById(state, 'bar')
      // Then
      expect(result).toBeDefined()
      expect(result).toEqual({ id: 'bar' })
      expect(result).toBe(state.data.bookings[1])
    })
  })

  describe('filterValidBookings', () => {
    it('remove offer from bookings, missing stock', () => {
      // given
      const bookingobj = {}
      // when
      const result = filterValidBookings(bookingobj)
      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
    it('remove offer from bookings, missing stock.resolvedOffer', () => {
      // given
      const booking = { stock: {} }
      // when
      const result = filterValidBookings(booking)
      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
    it('remove offer from bookings, missing stock.resolvedOffer.eventOrThing', () => {
      // given
      const booking = { stock: { resolvedOffer: {} } }
      // when
      const result = filterValidBookings(booking)
      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
    it('remove offer from bookings, missing stock.resolvedOffer.eventOrThing.type', () => {
      // given
      const booking = { stock: { resolvedOffer: { eventOrThing: {} } } }
      // when
      const result = filterValidBookings(booking)
      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
    it('do not remove offer from bookings, is not an activation type', () => {
      const booking = {
        stock: {
          resolvedOffer: {
            eventOrThing: { type: 'EventType.ANY' },
          },
        },
      }
      // when
      const result = filterValidBookings(booking)
      // then
      const expected = true
      expect(result).toStrictEqual(expected)
    })
    it('remove offer from bookings, is an activation type', () => {
      // given
      const booking = {
        stock: {
          resolvedOffer: {
            eventOrThing: {
              type: 'EventType.ACTIVATION',
            },
          },
        },
      }
      // when
      const result = filterValidBookings(booking)
      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
  })
  describe('filterBookingsInLessThanTwoDays', () => {
    it('returns an array of bookings with beginningDatetime today or in less than 2 days', () => {
      // given
      const nowMomentMock = moment()
      let allbookings = AllBookingsDataset(nowMomentMock)
      allbookings = allbookings.filter(filterValidBookings)
      // when
      const result = filterBookingsInLessThanTwoDays(allbookings, nowMomentMock)
      // then
      expect(result).toHaveLength(3)
      const expected = allbookings.filter(o => {
        const debugid = get(o, 'stock.debugid')
        return (
          debugid === 'not-activation-exact-now' ||
          debugid === 'not-activation-tomorrow' ||
          debugid === 'not-activation-in-exact-2-days'
        )
      })
      expect(result).toStrictEqual(expected)
    })
  })
  describe('filterBookingsInMoreThanTwoDaysOrPast', () => {
    it('returns all bookings excepts >= today hh:mm:s', () => {
      // given
      const nowMomentMock = moment()
      let allbookings = AllBookingsDataset(nowMomentMock)
      allbookings = allbookings.filter(filterValidBookings)
      // when
      const result = filterBookingsInMoreThanTwoDaysOrPast(
        allbookings,
        nowMomentMock
      )
      // then
      expect(result).toHaveLength(4)
      const expected = allbookings.filter(o => {
        const debugid = get(o, 'stock.debugid')
        return (
          debugid === 'not-activation-yesterday' ||
          debugid === 'not-activation-in-4-days' ||
          debugid === 'not-activation-in-2-days-and-1-seconds' ||
          debugid === 'not-activation-without-beginningDatetime'
        )
      })
      expect(result).toStrictEqual(expected)
    })
  })
})
