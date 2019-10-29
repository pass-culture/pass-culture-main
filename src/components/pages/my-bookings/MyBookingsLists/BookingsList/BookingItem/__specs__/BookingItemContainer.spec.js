import { mapStateToProps, mergeProps, ribbonLabelAndType } from '../BookingItemContainer'

describe('src | components | pages | my-bookings | MyBoolingsLists | BookingList | BookingItem | BookingItemContainer', () => {
  describe('mapStateToProps()', () => {
    let state
    let ownProps

    beforeEach(() => {
      state = {
        data: {
          features: [],
          mediations: [
            {
              id: 'AAAA',
            },
          ],
          offers: [
            {
              id: 'CCCC',
              product: { name: 'Fake booking name' },
              venue: {
                departementCode: '93',
              },
            },
          ],
          recommendations: [
            {
              id: 'AE',
              mediationId: 'AAAA',
              offerId: 'CCCC',
              thumbUrl: 'https://example.net/mediation/image',
            },
          ],
          stocks: [
            {
              id: 'AA',
              offerId: 'CCCC',
            },
          ],
        },
      }
      ownProps = {
        booking: {
          id: 'AE',
          isEventExpired: false,
          recommendationId: 'AE',
          stockId: 'AA',
          token: 'BBBB',
        },
        location: {
          pathname: '/reservations',
          search: '',
        },
      }
    })

    it('should return props with null ribbon', () => {
      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isQrCodeFeatureDisabled: true,
        mediation: {
          id: 'AAAA',
        },
        offer: {
          id: 'CCCC',
          product: { name: 'Fake booking name' },
          venue: {
            departementCode: '93',
          },
        },
        recommendation: {
          id: 'AE',
          mediationId: 'AAAA',
          offerId: 'CCCC',
          thumbUrl: 'https://example.net/mediation/image',
        },
        ribbon: null,
        stock: { id: 'AA', offerId: 'CCCC' },
      })
    })

    it('should return props with "retiré" ribbon when physical offer is used', () => {
      // given
      ownProps.booking.isUsed = true
      state.data.offers[0].isDigital = false
      state.data.offers[0].isEvent = false

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isQrCodeFeatureDisabled: true,
        mediation: {
          id: 'AAAA',
        },
        offer: {
          id: 'CCCC',
          isDigital: false,
          isEvent: false,
          product: { name: 'Fake booking name' },
          venue: {
            departementCode: '93',
          },
        },
        recommendation: {
          id: 'AE',
          mediationId: 'AAAA',
          offerId: 'CCCC',
          thumbUrl: 'https://example.net/mediation/image',
        },
        ribbon: {
          label: 'Retiré',
          type: 'finished',
        },
        stock: { id: 'AA', offerId: 'CCCC' },
      })
    })

    it('should return props with "utilisé" ribbon when digital offer is used', () => {
      // given
      ownProps.booking.isUsed = true
      state.data.offers[0].isDigital = true

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isQrCodeFeatureDisabled: true,
        mediation: {
          id: 'AAAA',
        },
        offer: {
          id: 'CCCC',
          isDigital: true,
          product: { name: 'Fake booking name' },
          venue: {
            departementCode: '93',
          },
        },
        recommendation: {
          id: 'AE',
          mediationId: 'AAAA',
          offerId: 'CCCC',
          thumbUrl: 'https://example.net/mediation/image',
        },
        ribbon: {
          label: 'Utilisé',
          type: 'finished',
        },
        stock: { id: 'AA', offerId: 'CCCC' },
      })
    })

    it('should return props with "terminé" ribbon when event is over', () => {
      // given
      ownProps.booking.isEventExpired = true

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isQrCodeFeatureDisabled: true,
        mediation: {
          id: 'AAAA',
        },
        offer: {
          id: 'CCCC',
          product: { name: 'Fake booking name' },
          venue: {
            departementCode: '93',
          },
        },
        recommendation: {
          id: 'AE',
          mediationId: 'AAAA',
          offerId: 'CCCC',
          thumbUrl: 'https://example.net/mediation/image',
        },
        ribbon: {
          label: 'Terminé',
          type: 'finished',
        },
        stock: { id: 'AA', offerId: 'CCCC' },
      })
    })

    it('should return props with "aujourd’hui" ribbon when booking is today', () => {
      // given
      const today = new Date()
      state.data.offers[0].isEvent = true
      state.data.stocks[0].beginningDatetime = today

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isQrCodeFeatureDisabled: true,
        mediation: {
          id: 'AAAA',
        },
        offer: {
          id: 'CCCC',
          isEvent: true,
          product: { name: 'Fake booking name' },
          venue: {
            departementCode: '93',
          },
        },
        recommendation: {
          id: 'AE',
          mediationId: 'AAAA',
          offerId: 'CCCC',
          thumbUrl: 'https://example.net/mediation/image',
        },
        ribbon: {
          label: 'Aujourd’hui',
          type: 'today',
        },
        stock: { beginningDatetime: today, id: 'AA', offerId: 'CCCC' },
      })
    })

    it('should return props with "demain" ribbon when booking is tomorrow', () => {
      // given
      const today = new Date()
      const tomorrow = new Date()
      tomorrow.setDate(today.getDate() + 1)
      state.data.offers[0].isEvent = true
      state.data.stocks[0].beginningDatetime = tomorrow

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isQrCodeFeatureDisabled: true,
        mediation: {
          id: 'AAAA',
        },
        offer: {
          id: 'CCCC',
          isEvent: true,
          product: { name: 'Fake booking name' },
          venue: {
            departementCode: '93',
          },
        },
        recommendation: {
          id: 'AE',
          mediationId: 'AAAA',
          offerId: 'CCCC',
          thumbUrl: 'https://example.net/mediation/image',
        },
        ribbon: {
          label: 'Demain',
          type: 'tomorrow',
        },
        stock: { beginningDatetime: tomorrow, id: 'AA', offerId: 'CCCC' },
      })
    })

    it('should return props with "annulé" ribbon when offer is cancelled', () => {
      // given
      ownProps.booking.isCancelled = true

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isQrCodeFeatureDisabled: true,
        mediation: {
          id: 'AAAA',
        },
        offer: {
          id: 'CCCC',
          product: { name: 'Fake booking name' },
          venue: {
            departementCode: '93',
          },
        },
        recommendation: {
          id: 'AE',
          mediationId: 'AAAA',
          offerId: 'CCCC',
          thumbUrl: 'https://example.net/mediation/image',
        },
        ribbon: {
          label: 'Annulé',
          type: 'cancelled',
        },
        stock: { id: 'AA', offerId: 'CCCC' },
      })
    })
  })

  describe('ribbonLabelAndType()', () => {
    describe('when the reservation is today', () => {
      it('should return an object with "Aujourd’hui" and "today"', () => {
        // given
        const isUsed = false
        const isCancelled = false
        const isPhysical = false
        const isDigital = false
        const isEventExpired = false
        const humanizeRelativeDate = 'Aujourd’hui'

        // when
        const ribbon = ribbonLabelAndType(
          isUsed,
          isCancelled,
          isPhysical,
          isDigital,
          isEventExpired,
          humanizeRelativeDate
        )

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
        const isPhysical = false
        const isDigital = false
        const isEventExpired = false
        const humanizeRelativeDate = 'Demain'

        // when
        const ribbon = ribbonLabelAndType(
          isUsed,
          isCancelled,
          isPhysical,
          isDigital,
          isEventExpired,
          humanizeRelativeDate
        )

        // then
        expect(ribbon).toStrictEqual({
          label: 'Demain',
          type: 'tomorrow',
        })
      })
    })

    describe('when the reservation is used', () => {
      it('should return nothing when offer is not passed', () => {
        // given
        const isUsed = true
        const isCancelled = false
        const isPhysical = false
        const isDigital = false
        const isEventExpired = false

        // when
        const ribbon = ribbonLabelAndType(
          isUsed,
          isCancelled,
          isPhysical,
          isDigital,
          isEventExpired
        )

        // then
        expect(ribbon).toBeNull()
      })

      it('should return an object with "Terminé" and "finished" when offer is passed', () => {
        // given
        const isUsed = false
        const isCancelled = false
        const isPhysical = false
        const isDigital = false
        const isEventExpired = true

        // when
        const ribbon = ribbonLabelAndType(
          isUsed,
          isCancelled,
          isPhysical,
          isDigital,
          isEventExpired
        )

        // then
        expect(ribbon).toStrictEqual({
          label: 'Terminé',
          type: 'finished',
        })
      })

      it('should return an object with "Retiré" and "finished" for physcical offer', () => {
        // given
        const isUsed = true
        const isCancelled = false
        const isDigital = false
        const isPhysical = true
        const isEventExpired = false

        // when
        const ribbon = ribbonLabelAndType(
          isUsed,
          isCancelled,
          isPhysical,
          isDigital,
          isEventExpired
        )

        // then
        expect(ribbon).toStrictEqual({
          label: 'Retiré',
          type: 'finished',
        })
      })

      it('should return an object with "Utilisé" and "finished" for numeric offer', () => {
        // given
        const isUsed = true
        const isCancelled = false
        const isDigital = true
        const isPhysical = false
        const isEventExpired = false

        // when
        const ribbon = ribbonLabelAndType(
          isUsed,
          isCancelled,
          isPhysical,
          isDigital,
          isEventExpired
        )

        // then
        expect(ribbon).toStrictEqual({
          label: 'Utilisé',
          type: 'finished',
        })
      })
    })

    describe('when the reservation is cancelled', () => {
      it('should return an object with "Annulé" and "cancelled"', () => {
        // given
        const isUsed = false
        const isCancelled = true

        // when
        const ribbon = ribbonLabelAndType(isUsed, isCancelled)

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

        // when
        const ribbon = ribbonLabelAndType(isUsed, isCancelled)

        // then
        expect(ribbon).toBeNull()
      })
    })
  })

  describe('mergeProps', () => {
    it('should spread stateProps, dispatchProps and ownProps into mergedProps', () => {
      // given
      const stateProps = {
        offer: { id: 'B4' },
      }
      const dispatchProps = {
        dispatchFunction: () => {},
      }
      const ownProps = {
        location: {
          href: '/src/here',
        },
      }

      // when
      const mergedProps = mergeProps(stateProps, dispatchProps, ownProps)

      // then
      expect(mergedProps).toStrictEqual({
        offer: { id: 'B4' },
        dispatchFunction: expect.any(Function),
        location: {
          href: '/src/here',
        },
        trackConsultOffer: expect.any(Function),
      })
    })

    it('should map a tracking event for consulting an offer', () => {
      // given
      const stateProps = {
        offer: { id: 'B4' },
      }
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }

      // when
      mergeProps(stateProps, {}, ownProps).trackConsultOffer()

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'consultOffer',
        name: 'B4',
      })
    })
  })
})
