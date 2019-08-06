import { mapStateToProps, ribbonLabelAndType } from '../BookingItemContainer'

describe('src | components | pages | my-bookings | MyBoolingsLists | BookingList | BookingItem | BookingItemContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return props with date elements', () => {
      // given
      const bookingId = 'AE'
      const token = 'BBBB'
      const offerId = 'CCCC'
      const isCancelled = true
      const mediationId = 'AAAA'
      const departementCode = '93'
      const productName = 'Fake booking name'
      const beginningDatetime = '2019-05-15T20:00:00Z'
      const pathname = '/reservations'
      const search = ''
      const thumbUrl = 'https://example.net/mediation/image'
      const mediation = {
        id: mediationId,
      }
      const isFinished = false
      const offer = {
        id: offerId,
        isEvent: true,
        isFinished,
        product: { name: productName },
        venue: {
          departementCode,
        },
      }
      const recommendationId = 'AE'
      const recommendation = {
        id: recommendationId,
        mediationId,
        offerId,
        thumbUrl,
      }
      const state = {
        data: {
          mediations: [mediation],
          offers: [offer],
          recommendations: [recommendation],
        },
      }
      const ownProps = {
        booking: {
          id: bookingId,
          isCancelled,
          recommendationId,
          stock: {
            beginningDatetime,
            offerId,
          },
          token,
        },
        location: {
          pathname,
          search,
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      const expected = {
        isFinished,
        mediation,
        offer,
        recommendation,
        ribbon: {
          label: 'Annulé',
          type: 'cancelled',
        },
      }
      expect(props).toStrictEqual(expected)
    })
  })

  describe('ribbonLabelAndType()', () => {
    describe('when the reservation is today', () => {
      it('should return an object with "Aujourd’hui" et "today"', () => {
        // given
        const isUsed = false
        const isCancelled = false
        const isFinished = false
        const humanizeRelativeDate = 'Aujourd’hui'

        // when
        const ribbon = ribbonLabelAndType(isUsed, isCancelled, isFinished, humanizeRelativeDate)

        // then
        expect(ribbon).toStrictEqual({
          label: 'Aujourd’hui',
          type: 'today',
        })
      })
    })

    describe('when the reservation is tomorrow', () => {
      it('should return an object with "Demain" and "tomorrow"', () => {
        // given
        const isUsed = false
        const isCancelled = false
        const isFinished = false
        const humanizeRelativeDate = 'Demain'

        // when
        const ribbon = ribbonLabelAndType(isUsed, isCancelled, isFinished, humanizeRelativeDate)

        // then
        expect(ribbon).toStrictEqual({
          label: 'Demain',
          type: 'tomorrow',
        })
      })
    })

    describe('when the reservation is used', () => {
      it('should return an object with "Terminé" et "finished"', () => {
        // given
        const isUsed = true
        const isCancelled = false
        const isFinished = false

        // when
        const ribbon = ribbonLabelAndType(isUsed, isCancelled, isFinished)

        // then
        expect(ribbon).toStrictEqual({
          label: 'Terminé',
          type: 'finished',
        })
      })
    })

    describe('when the reservation is finished', () => {
      it('should return an object with "Terminé" et "finished"', () => {
        // given
        const isUsed = false
        const isCancelled = false
        const isFinished = true

        // when
        const ribbon = ribbonLabelAndType(isUsed, isCancelled, isFinished)

        // then
        expect(ribbon).toStrictEqual({
          label: 'Terminé',
          type: 'finished',
        })
      })
    })

    describe('when the reservation is cancelled', () => {
      it('should return an object with "Annulé" et "cancelled"', () => {
        // given
        const isUsed = false
        const isCancelled = true
        const isFinished = false

        // when
        const ribbon = ribbonLabelAndType(isUsed, isCancelled, isFinished)

        // then
        expect(ribbon).toStrictEqual({
          label: 'Annulé',
          type: 'cancelled',
        })
      })
    })

    describe('when the reservation is in progress', () => {
      it('should return null', () => {
        // given
        const isUsed = false
        const isCancelled = false
        const isFinished = false

        // when
        const ribbon = ribbonLabelAndType(isUsed, isCancelled, isFinished)

        // then
        expect(ribbon).toBeNull()
      })
    })
  })
})
