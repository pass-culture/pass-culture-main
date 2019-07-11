import moment from 'moment'

import { allBookingsDataset, inExactTwoDays } from './data/selectBookings'
import {
  filterValidBookings,
  filterBookingsInLessThanTwoDays,
  filterBookingsInMoreThanTwoDaysOrPast,
  selectBookingById,
} from '../selectBookings'

describe('src | selectors | selectBookings', () => {
  describe('selectBookingById', () => {
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
      expect(result).toStrictEqual({ id: 'bar' })
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

    it('remove offer from bookings, missing stock.resolvedOffer.type', () => {
      // given
      const booking = { stock: { resolvedOffer: {} } }

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
            type: 'EventType.ANY',
          },
        },
      }

      // when
      const result = filterValidBookings(booking)

      // then
      const expected = true
      expect(result).toStrictEqual(expected)
    })

    it('remove offer from bookings, is an activation type (event)', () => {
      // given
      const booking = {
        stock: {
          resolvedOffer: {
            type: 'EventType.ACTIVATION',
          },
        },
      }

      // when
      const result = filterValidBookings(booking)

      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })

    it('remove offer from bookings, is an activation type (thing)', () => {
      // given
      const booking = {
        stock: {
          resolvedOffer: {
            type: 'ThingType.ACTIVATION',
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
      const now = moment()
      const allBookings = allBookingsDataset(now)

      // when
      const results = filterBookingsInLessThanTwoDays(allBookings, now)

      // then
      expect(results).toHaveLength(4)
      expect(
        results.every(
          booking => booking.stock.beginningDatetime <= inExactTwoDays(now)
        )
      ).toBe(true)
    })
  })

  describe('filterBookingsInMoreThanTwoDaysOrPast', () => {
    it('returns all bookings excepts >= today hh:mm:s', () => {
      // given
      const now = moment()
      const allBookings = allBookingsDataset(now).filter(filterValidBookings)

      // when
      const results = filterBookingsInMoreThanTwoDaysOrPast(allBookings, now)

      // then
      expect(results).toHaveLength(4)
      expect(
        results.every(booking => {
          const date = booking.stock.beginningDatetime
          return date > inExactTwoDays(now) || date < now
        })
      ).toBe(true)
    })
  })
})
