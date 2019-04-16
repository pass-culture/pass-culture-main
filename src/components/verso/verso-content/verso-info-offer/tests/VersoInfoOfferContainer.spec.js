import { mapStateToProps } from '../VersoInfoOfferContainer'

describe('src | components | verso | verso-content | verso-info-offer | VersoInfoOfferContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object containing bookables, current recommendation and information regarding the offer expiration', () => {
      // given
      const initialState = {
        data: {
          bookings: [],
          recommendations: [
            {
              mediationId: 2,
              offer: {
                isFinished: false,
                stocks: [{}],
              },
              offerId: 1,
              uniqId: 3,
            },
          ],
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
      }

      // when
      const result = mapStateToProps(initialState, props)

      // then
      expect(result.bookables).not.toBe(null)
      expect(result.isFinished).toBe(false)
      expect(result.recommendation).not.toBe(null)
    })
  })
})
