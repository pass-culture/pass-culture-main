import { mapStateToProps } from '../VersoContentOfferContainer'

describe('src | components | verso | verso-content | verso-info-offer | VersoContentOfferContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object containing bookables, current recommendation and information regarding the offer expiration', () => {
      // given
      const recommendation = {
        mediationId: 2,
        offerId: 1,
        uniqId: 3,
      }
      const state = {
        data: {
          bookings: [],
          favorites: [],
          mediations: [
            {
              id: 2,
            },
          ],
          offers: [
            {
              id: 1,
              isNotBookable: false,
              stocks: [{}],
              venue: {
                latitude: 48.91683,
                longitude: 2.4388,
              },
            },
          ],
          recommendations: [recommendation],
          stocks: [{ offerId: 1 }],
        },
        geolocation: {
          latitude: 41.1,
          longitude: 42.1,
        },
      }
      const props = {
        match: {
          params: { mediationId: 2, offerId: 1 },
          url: 'this is a fake url',
        },
        recommendation,
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result.bookables).not.toBeNull()
      expect(result.isNotBookable).toBe(false)
      expect(result.recommendation).not.toBeNull()
    })
  })
})
