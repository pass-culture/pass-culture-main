import {
  stringify,
  updatePropsWithDateElements,
  urlOf,
  mapStateToProps,
} from '../MyBookingContainer'

describe('src | components | pages | my-bookings | MyBookingContainer', () => {
  describe('stringify()', () => {
    it('should stringify and capitalize a date with a time zone', () => {
      // given
      const date = '2019-07-08T20:00:00Z'
      const timeZone = 'Europe/Paris'

      // when
      const stringifyDate = stringify(date)(timeZone)

      // then
      expect(stringifyDate).toBe('Lundi 08/07/2019 à 22:00')
    })
  })

  describe('updateProps()', () => {
    it('should add some element of date thanks to time zone within props', () => {
      // given
      const props = {}
      const beginningDateTime = '2019-05-15T20:00:00Z'
      const departementCode = '93'

      // when
      const updatedProps = updatePropsWithDateElements(props, beginningDateTime, departementCode)

      // then
      expect(updatedProps).toStrictEqual({
        stringifyDate: 'Mercredi 15/05/2019 à 22:00',
      })
    })
  })

  describe('urlOf()', () => {
    it('should return a URL of offer verso with offerId and mediationId', () => {
      // given
      const booking = {
        recommendation: {
          mediationId: 'FA',
        },
        stock: {
          resolvedOffer: {
            id: 'ME',
          },
        },
      }

      // when
      const offerVersoUrl = urlOf(booking)

      // then
      expect(offerVersoUrl).toBe(`/decouverte/ME/FA/verso`)
    })

    it('should return a URL of offer verso with just offerId', () => {
      // given
      const booking = {
        recommendation: {
          mediationId: null,
        },
        stock: {
          resolvedOffer: {
            id: 'ME',
          },
        },
      }

      // when
      const offerVersoUrl = urlOf(booking)

      // then
      expect(offerVersoUrl).toBe(`/decouverte/ME/verso`)
    })
  })

  describe('mapStateToProps()', () => {
    it('should return props with date elements', () => {
      // given
      const token = 'BBBB'
      const offerId = 'CCCC'
      const isCancelled = true
      const mediationId = 'AAAA'
      const departementCode = '93'
      const name = 'Fake booking name'
      const beginningDateTime = '2019-05-15T20:00:00Z'
      const thumbUrl = 'https://example.net/mediation/image'
      const ownProps = {
        booking: {
          isCancelled,
          recommendation: { mediationId, thumbUrl },
          stock: {
            beginningDatetime: beginningDateTime,
            resolvedOffer: {
              id: offerId,
              isEvent: true,
              product: { name },
              venue: { departementCode },
            },
          },
          token,
        },
      }

      // when
      const props = mapStateToProps({}, ownProps)

      // then
      const offerVersoUrl = `/decouverte/${offerId}/${mediationId}/verso`
      const stringifyDate = 'Mercredi 15/05/2019 à 22:00'
      const expected = {
        isCancelled,
        name,
        offerVersoUrl,
        stringifyDate,
        thumbUrl,
        token: 'bbbb',
      }
      expect(props).toStrictEqual(expected)
    })
  })
})
