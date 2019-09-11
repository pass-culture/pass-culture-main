import {
  mapStateToProps,
  mapDispatchToProps,
  mergeProps,
  ribbonLabelAndType,
} from '../BookingItemContainer'

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
          stocks: [{ id: 'AA', offerId, beginningDatetime }],
        },
      }
      const ownProps = {
        booking: {
          id: bookingId,
          isCancelled,
          recommendationId,
          stockId: 'AA',
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
      expect(props).toStrictEqual({
        isFinished,
        mediation,
        offer,
        recommendation,
        ribbon: {
          label: 'Annulé',
          type: 'cancelled',
        },
        stock: { beginningDatetime: '2019-05-15T20:00:00Z', id: 'AA', offerId: 'CCCC' },
      })
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

  describe('mapDescribeToProps', () => {
    describe('when mapping trackConsultOffer', () => {
      it('should dispatch a track Matomo Event with correct arguments', () => {
        // given
        const ownProps = {
          tracking: {
            trackEvent: jest.fn(),
          },
        }
        // when
        mapDispatchToProps(undefined, ownProps).trackConsultOffer('B4')

        // then
        expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
          action: 'consultOffer',
          name: 'B4',
        })
      })
    })
  })

  describe('mergeProps', () => {
    it('should spread all stateProps and dispatch props into mergedProps', () => {
      // given
      const stateProps = {
        offer: { id: 'B4' },
      }
      const dispatchProps = {
        trackConsultOffer: () => {},
      }

      // when
      const mergedProps = mergeProps(stateProps, dispatchProps)

      // then
      expect(mergedProps).toStrictEqual({
        offer: { id: 'B4' },
        trackConsultOffer: expect.any(Function),
      })
    })

    it('should wrap trackConsultOffer with offerId from stateProps', () => {
      // given
      const stateProps = {
        offer: { id: 'B4' },
      }
      const dispatchProps = {
        trackConsultOffer: jest.fn(),
      }

      // when
      mergeProps(stateProps, dispatchProps).trackConsultOffer()

      // then
      expect(dispatchProps.trackConsultOffer).toHaveBeenCalledWith('B4')
    })
  })
})
