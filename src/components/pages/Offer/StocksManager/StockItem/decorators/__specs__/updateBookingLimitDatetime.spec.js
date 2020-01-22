import updateBookingLimitDatetime from '../updateBookingLimitDatetime'

describe('src | components | pages | Offer | StockManager | StockItem | decorators | updateBookingLimitDatetime', () => {
  describe('for an event product case', () => {
    describe('when booking limit date is at least one day before beginning date then booking limit time is forced to be at 23h59', () => {
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
        expect(result.bookingLimitDatetime).toStrictEqual('2019-04-20T21:59:00.000Z')
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
        expect(result.bookingLimitDatetime).toStrictEqual('2019-04-21T02:59:00.000Z')
      })
    })

    describe('when booking limit date is changed to be on the same day as beginning date then booking limit time is equal to beginning time', () => {
      it('should make bookingLimitDatetime equal to beginningDatetime (whatever the timezone)', () => {
        // given
        const isEvent = true
        const beginningDatetime = '2019-04-20T19:00:00.000Z'
        const bookingLimitDatetime = '2019-04-20T15:00:00.000Z'
        const previousBeginninDatetime = beginningDatetime
        const previousBookingLimitDatetime = '2019-04-10T15:00:00.000Z'

        // when
        const result = updateBookingLimitDatetime({
          beginningDatetime,
          bookingLimitDatetime,
          isEvent,
          previousBeginninDatetime,
          previousBookingLimitDatetime,
        })

        // then
        expect(result.bookingLimitDatetime).toStrictEqual('2019-04-20T19:00:00.000Z')
      })
    })

    describe('when booking limit date is changed to be on the same day as beginning date', () => {
      describe('when user change beginning time', () => {
        it('should update bookingLimitDatetime with new time', () => {
          // given
          const isEvent = true
          const beginningDatetime = '2020-01-18T19:00:59.984000Z'
          const bookingLimitDatetime = 'XXXXXXX'
          const beginningTime = '12:00'

          const previousBeginningTime = '20:00'
          const previousBeginninDatetime = beginningDatetime
          const previousBookingLimitDatetime = '2020-01-18T19:00:59.984000Z'

          // when
          const result = updateBookingLimitDatetime({
            beginningDatetime,
            beginningTime,
            bookingLimitDatetime,
            isEvent,
            previousBeginningTime,
            previousBeginninDatetime,
            previousBookingLimitDatetime,
          })

          // then
          expect(result.bookingLimitDatetime).toStrictEqual('2020-01-18T11:00:59.984Z')
        })
      })
    })
  })

  describe('for a thing product case', () => {
    it('when booking limit date is not empty then booking limit time is equal to 23h59 minus 1 or 2 hours for europe/paris (because utc)', () => {
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
      expect(result.bookingLimitDatetime).toStrictEqual('2019-04-27T21:59:00.000Z')
    })
    it('when booking limit date is not empty then booking limit time is equal to 23h59 plus 3 hours for america/cayenne (because utc)', () => {
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
      expect(result.bookingLimitDatetime).toStrictEqual('2019-04-28T02:59:00.000Z')
    })
  })
})
