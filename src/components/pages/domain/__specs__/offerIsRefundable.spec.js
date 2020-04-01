import offerIsRefundable from '../offerIsRefundable'

describe('src | components | pages | Offer | domain | offerIsRefundable', () => {
  let venue

  describe('when venue is physical', () => {
    beforeEach(() => {
      venue = {
        isVirtual: false,
      }
    })

    it('offer is refundable', () => {
      // when
      const musicInstrumentType = {
        offlineOnly: true,
        onlineOnly: false,
        value: 'ThingType.INSTRUMENT',
      }

      // then
      expect(offerIsRefundable(musicInstrumentType, venue)).toBe(true)
    })
  })

  describe('when venue is digital', () => {
    beforeEach(() => {
      venue = {
        isVirtual: true,
      }
    })

    describe('when offer type is another than cinema card and book', () => {
      it('offer is not refundable', () => {
        // when
        const gameType = {
          value: 'ThingType.JEUX_VIDEO',
        }

        // then
        expect(offerIsRefundable(gameType, venue)).toBe(false)
      })
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
        expect(offerIsRefundable(bookType, venue)).toBe(true)
      })
    })

    describe('when offer type is a cinema card', () => {
      it('offer is refundable', () => {
        // when
        const cinemaCardType = {
          offlineOnly: false,
          onlineOnly: true,
          value: 'ThingType.CINEMA_CARD',
        }

        // then
        expect(offerIsRefundable(cinemaCardType, venue)).toBe(true)
      })
    })
  })
})
