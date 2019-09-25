import { mapStateToProps } from '../TiteLiveInformationContainer'

describe('src | components | pages | Offer | TiteLiveInformation | TiteLiveInformationContainer', () => {
  let state
  let props

  beforeEach(() => {
    state = {
      data: {
        offers: [{ id: 'UU', isEvent: true, isThing: false, venueId: 'EFGH' }],
      },
    }
    props = {
      match: {},
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      props = {
        match: {
          params: {
            offerId: 'UU',
          },
        },
        offererId: 'ABCD',
        product: {
          id: 'ART',
          thumbUrl: 'http://localhost/storage/thumbs/products/AERTR',
        },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        offererId: 'ABCD',
        thumbUrl: 'http://localhost/storage/thumbs/products/AERTR',
        venueId: 'EFGH',
      })
    })
  })
})
