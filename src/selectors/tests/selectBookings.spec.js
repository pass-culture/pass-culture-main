// jest --env=jsdom ./src/selectors/tests/selectBookings --watch
import moment from 'moment'
import get from 'lodash.get'

import AllBookingsDataset from './data/selectBookings'
import {
  filterBookingsActivationOfTypeThing,
  filterBookingsInLessThanTwoDays,
  removePastBookings,
  filterBookingsInMoreThanTwoDays,
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
  describe('filterBookingsActivationOfTypeThing', () => {
    it('returns false, missing stock', () => {
      // given
      const booking = {}
      // when
      const result = filterBookingsActivationOfTypeThing(booking)
      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
    it('returns false, missing stock.resolvedOffer', () => {
      // given
      const booking = { stock: {} }
      // when
      const result = filterBookingsActivationOfTypeThing(booking)
      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
    it('returns false, missing stock.resolvedOffer.eventOrThing', () => {
      // given
      const booking = { stock: { resolvedOffer: {} } }
      // when
      const result = filterBookingsActivationOfTypeThing(booking)
      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
    it('returns false, missing stock.resolvedOffer.eventOrThing.type', () => {
      // given
      const booking = { stock: { resolvedOffer: { eventOrThing: {} } } }
      // when
      const result = filterBookingsActivationOfTypeThing(booking)
      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
    it('returns true, type is not an activation type', () => {
      const booking = {
        stock: {
          resolvedOffer: { eventOrThing: { type: 'EventType.ANY' } },
        },
      }
      // when
      const result = filterBookingsActivationOfTypeThing(booking)
      // then
      const expected = true
      expect(result).toStrictEqual(expected)
    })
    it('returns false, is an activation type and a thing/numeric offer', () => {
      // given
      const booking = {
        stock: {
          resolvedOffer: {
            eventOrThing: {
              type: 'EventType.ACTIVATION',
            },
            offerId: null,
            thingId: 1234,
          },
        },
      }
      // when
      const result = filterBookingsActivationOfTypeThing(booking)
      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
    it('returns true, is an activation type and not a thing/numeric offer', () => {
      // given
      const booking = {
        stock: {
          resolvedOffer: {
            eventOrThing: {
              type: 'EventType.ACTIVATION',
            },
            offerId: 1234,
            thingId: null,
          },
        },
      }
      // when
      const result = filterBookingsActivationOfTypeThing(booking)
      // then
      const expected = true
      expect(result).toStrictEqual(expected)
    })
  })
  describe('filterBookingsInLessThanTwoDays', () => {
    it('returns an array of bookings with beginningDatetime <= 2 days', () => {
      // given
      const momentNowMock = moment()
      const allbookings = AllBookingsDataset(momentNowMock)
      // when
      const result = filterBookingsInLessThanTwoDays(allbookings, momentNowMock)
      // then
      const expected = allbookings.filter(o => {
        const debugid = get(o, 'stock.eventOccurrence.debugid')
        return (
          debugid === 'yesterday' ||
          debugid === 'in-exact-2-days' ||
          debugid === 'tomorrow'
        )
      })
      expect(result).toHaveLength(3)
      expect(result).toStrictEqual(expected)
    })
  })
  describe('removePastBookings', () => {
    it('returns all bookings excepts >= today hh:mm:s', () => {
      // given
      const momentNowMock = moment()
      const allbookings = AllBookingsDataset(momentNowMock)
      // when
      const result = removePastBookings(allbookings, momentNowMock)
      // then
      const expected = allbookings.filter(o => {
        const debugid = get(o, 'stock.eventOccurrence.debugid')
        return (
          debugid === 'in-4-days' ||
          debugid === 'in-2-days-and-1-seconds' ||
          debugid === 'in-exact-2-days' ||
          debugid === 'tomorrow'
        )
      })
      expect(result).toHaveLength(4)
      expect(result).toStrictEqual(expected)
    })
  })
  describe('filterBookingsInMoreThanTwoDays', () => {
    it('returns all bookings excepts >= today hh:mm:s', () => {
      // given
      const momentNowMock = moment()
      const allbookings = AllBookingsDataset(momentNowMock.clone())
      // when
      const result = filterBookingsInMoreThanTwoDays(allbookings, momentNowMock)
      // then
      const expected = allbookings.filter(o => {
        const debugid = get(o, 'stock.eventOccurrence.debugid')
        return debugid === 'in-4-days' || debugid === 'in-2-days-and-1-seconds'
      })
      expect(result).toHaveLength(2)
      expect(result).toStrictEqual(expected)
    })
  })
})
