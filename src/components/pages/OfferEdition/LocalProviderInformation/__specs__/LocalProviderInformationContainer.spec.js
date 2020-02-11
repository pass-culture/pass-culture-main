import { mapStateToProps } from '../LocalProviderInformationContainer'

describe('src | components | pages | Offer | LocalProviderInformation | LocalProviderInformationContainer', () => {
  let state
  let props

  beforeEach(() => {
    state = {
      data: {
        offers: [{ id: 'UU', name: 'Super Livre', isEvent: true, isThing: false, venueId: 'EFGH', productId: 'AGDK' }],
        products: [{id: 'AGDK', thumbUrl: 'http://localhost/storage/thumbs/products/AERTR'}]
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
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        offererId: 'ABCD',
        offerName: 'Super Livre',
        providerInfo: {icon: 'logo-titeLive', name: 'Tite Live'},
        thumbUrl: 'http://localhost/storage/thumbs/products/AERTR',
        venueId: 'EFGH',
      })
    })
  })
})
