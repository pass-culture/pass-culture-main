import { updateBookingLimitDatetime } from '../adaptBookingLimitDatetimeGivenBeginningDatetime'

describe('src | components | pages | Offer | StockManager | StockItem | decorators | updateBookingLimitDatetime', () => {
  describe('for an event product case', () => {
    describe('when booking limit date is at least one day before beginning date', () => {
      it('should return 23h59 minus 1 or 2 hours for europe/paris (because utc)', () => {
        // given
        const isEvent = true
        const beginningDatetime = '2019-04-28T19:00:00.000Z'
        const bookingLimitDatetime = '2019-04-20T15:00:00.000Z'

        // when
        const result = updateBookingLimitDatetime({
          beginningDatetime,
          bookingLimitDatetime,
          isEvent,
          timezone: 'Europe/Paris',
        })

        // then
        expect(result.bookingLimitDatetime).toBe('2019-04-20T21:59:00.000Z')
      })

      it('should return 23h59 plus 3 hours for america/cayenne (because utc)', () => {
        // given
        const isEvent = true
        const beginningDatetime = '2019-04-28T19:00:00.000Z'
        const bookingLimitDatetime = '2019-04-20T15:00:00.000Z'

        // when
        const result = updateBookingLimitDatetime({
          beginningDatetime,
          bookingLimitDatetime,
          isEvent,
          timezone: 'America/Cayenne',
        })

        // then
        expect(result.bookingLimitDatetime).toBe('2019-04-21T02:59:00.000Z')
      })
    })

    describe('when booking limit date is changed to be on the same day as beginning date', () => {
      it('should make the booking limit date time equal to the beginning date time (whatever the timezone)', () => {
        // given
        const isEvent = true
        const beginningDatetime = '2019-04-20T19:00:00.000Z'
        const bookingLimitDatetime = '2019-04-20T15:00:00.000Z'

        // when
        const result = updateBookingLimitDatetime({
          beginningDatetime,
          bookingLimitDatetime,
          isEvent,
        })

        // then
        expect(result.bookingLimitDatetime).toBe('2019-04-20T19:00:00.000Z')
      })
    })

    describe('when the booking limit date time is undefined', () => {
      it('should make the booking limit date time equal to the beginning date time (whatever the timezone)', () => {
        // given
        const isEvent = true
        const beginningDatetime = '2019-04-20T19:00:00.000Z'
        const bookingLimitDatetime = null

        // when
        const result = updateBookingLimitDatetime({
          beginningDatetime,
          bookingLimitDatetime,
          isEvent,
        })

        // then
        expect(result.bookingLimitDatetime).toBe('2019-04-20T19:00:00.000Z')
      })
    })

    describe('when booking limit date time is empty', () => {
      it('should leave booking limit date time empty', () => {
        // given
        const isEvent = true
        const beginningDatetime = '2019-04-20T19:00:00.000Z'
        const bookingLimitDatetime = ''

        // when
        const result = updateBookingLimitDatetime({
          beginningDatetime,
          bookingLimitDatetime,
          isEvent,
        })

        // then
        expect(result.bookingLimitDatetime).toBe('')
      })
    })
  })

  describe('for a thing product case', () => {
    describe('for europe/paris (because utc)', () => {
      it('should update booking limit time to 23h59 minus 1 or 2 hours', () => {
        // given
        const isEvent = false
        const bookingLimitDatetime = '2019-04-27T19:00:00.000Z'

        // when
        const result = updateBookingLimitDatetime({
          bookingLimitDatetime,
          isEvent,
          timezone: 'Europe/Paris',
        })

        // then
        expect(result.bookingLimitDatetime).toBe('2019-04-27T21:59:00.000Z')
      })
    })

    describe('for america/cayenne (because utc)', () => {
      it('should update booking limit time to 23h59 plus 3 hours', () => {
        // given
        const isEvent = false
        const bookingLimitDatetime = '2019-04-27T19:00:00.000Z'

        // when
        const result = updateBookingLimitDatetime({
          bookingLimitDatetime,
          isEvent,
          timezone: 'America/Cayenne',
        })

        // then
        expect(result.bookingLimitDatetime).toBe('2019-04-28T02:59:00.000Z')
      })
    })

    describe('when booking limit date time is empty', () => {
      it('should make booking limit date time null', () => {
        // given
        const isEvent = false
        const bookingLimitDatetime = null

        // when
        const result = updateBookingLimitDatetime({
          bookingLimitDatetime,
          isEvent,
        })

        // then
        expect(result.bookingLimitDatetime).toBeNull()
      })
    })
  })
})
