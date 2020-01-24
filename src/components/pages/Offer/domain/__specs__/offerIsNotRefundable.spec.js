import offerIsNotRefundable from '../offerIsNotRefundable'

describe('src | components | pages | Offer | domain | getDurationInHours', () => {
  let venue

  describe('when no type and no venue', () => {
    it('should return false by defaut', () => {
      expect(offerIsNotRefundable()).toBe(false)
    })
  })

  describe('when venue is digital', () => {
    beforeEach(() => {
      venue = {
        isVirtual: true,
      }
    })

    describe('when offer type is a book', () => {
      it('offer is refundable', () => {
        // when
        const bookType = {
          offlineOnly: false,
          onlineOnly: false,
          value: 'ThingType.LIVRE_EDITION',
        }

        // then
        expect(offerIsNotRefundable(bookType, venue)).toBe(false)
      })
    })

    describe('when offer type is a cinema card', () => {
      it('offer is refundable', function() {
        // when
        const cinemaCardType = {
          offlineOnly: false,
          onlineOnly: true,
          value: 'ThingType.CINEMA_CARD',
        }

        // then
        expect(offerIsNotRefundable(cinemaCardType, venue)).toBe(false)
      })
    })

    describe('when offer type is available online or offline ', () => {
      it('offer is not refundable', () => {
        // when
        const musicType = {
          offlineOnly: false,
          onlineOnly: false,
          value: 'ThingType.MUSIQUE',
        }

        // then
        expect(offerIsNotRefundable(musicType, venue)).toBe(true)
      })
    })

    describe('when offer type is available online only', () => {
      it('offer is not refundable', () => {
        // when
        const gameType = {
          offlineOnly: false,
          onlineOnly: true,
          value: 'ThingType.JEUX_VIDEO',
        }

        // then
        expect(offerIsNotRefundable(gameType, venue)).toBe(true)
      })
    })
  })

  describe('when venue is physical', () => {
    beforeEach(() => {
      venue = {
        isVirtual: false,
      }
    })
    describe('when offer type is not digital at all', () => {
      it('should not display digital offer information message', () => {
        // when
        const musicInstrumentType = {
          offlineOnly: true,
          onlineOnly: false,
          value: 'ThingType.INSTRUMENT',
        }

        // then
        expect(offerIsNotRefundable(musicInstrumentType, venue)).toBe(false)
      })
    })

    describe('when offer type is a book', () => {
      it('should not display digital offer information message', () => {
        // when
        const bookType = {
          offlineOnly: false,
          onlineOnly: false,
          value: 'ThingType.LIVRE_EDITION',
        }

        // then
        expect(offerIsNotRefundable(bookType, venue)).toBe(false)
      })
    })

    describe('when offer type is available online or offline', () => {
      it('should not display digital offer information message', () => {
        // when
        const audioVisualType = {
          offlineOnly: false,
          onlineOnly: false,
          value: 'ThingType.AUDIOVISUEL',
        }

        // then
        expect(offerIsNotRefundable(audioVisualType, venue)).toBe(false)
      })
    })
  })
})
