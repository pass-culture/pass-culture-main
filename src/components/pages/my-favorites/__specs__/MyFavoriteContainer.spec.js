import {
  stringify,
  updatePropsWithDateElements,
  urlOf,
  mapStateToProps,
} from '../MyFavoriteContainer'

describe('src | components | pages | my-favorite | MyBookingFavorite', () => {
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
      const favorite = {
        offerId: 'ME',
        offer: {
          id: 'ME',
        },
        mediationId: 'FA',
        mediation: {
          id: 'FA'
        },
      }

      // when
      const offerVersoUrl = urlOf(favorite)

      // then
      expect(offerVersoUrl).toBe(`/decouverte/ME/FA/verso`)
    })

    it('should return a URL of offer verso with just offerId', () => {
      // given
      const favorite = {
        offerId: 'ME',
        offer: {
          id: 'ME',
        },
        mediationId: null,
        mediation: {
          id: null
        },
      }

      // when
      const offerVersoUrl = urlOf(favorite)

      // then
      expect(offerVersoUrl).toBe(`/decouverte/ME/verso`)
    })
  })

  describe('mapStateToProps()', () => {
    it('should return props with date elements', () => {
      // given
      const offerId = 'CCCC'
      const isCancelled = true
      const mediationId = 'AAAA'
      const name = 'Fake booking name'
      const thumbUrl = 'https://example.net/mediation/image'
      const ownProps = {
        favorite: {
          offerId: { offerId },
          offer: {
            id: { offerId },
            name: { name }
          },
          mediationId: { mediationId },
          mediation: {
            id: { mediationId },
            thumbUrl: { thumbUrl }
          },
        },
      }

      // when
      const props = mapStateToProps({}, ownProps)

      // then
      const offerVersoUrl = `/decouverte/${offerId}/${mediationId}/verso`
      const stringifyDate = 'Mercredi 15/05/2019 à 22:00'
      const expected = {
        name,
        offerVersoUrl,
        stringifyDate,
        thumbUrl,
      }
      expect(props).toStrictEqual(expected)
    })
  })
})
