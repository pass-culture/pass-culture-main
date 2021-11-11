import { mapStateToProps } from '../VersoContentOfferContainer'

describe('src | components | verso | verso-content | verso-info-offer | VersoContentOfferContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object containing bookables and information regarding the offer expiration', () => {
      // given
      const state = {
        data: {
          bookings: [],
          categories: [
            {
              categories: [],
              subcategories: [],
            },
          ],
          favorites: [],
          mediations: [
            {
              id: 2,
            },
          ],
          offers: [
            {
              id: 1,
              isBookable: true,
              stocks: [{}],
              venue: {
                latitude: 48.91683,
                longitude: 2.4388,
              },
            },
          ],
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
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result.bookables).not.toBeNull()
      expect(result.isBookable).toBe(true)
    })
  })
})
