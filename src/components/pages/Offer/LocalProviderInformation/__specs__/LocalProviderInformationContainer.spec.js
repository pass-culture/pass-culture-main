import { getProviderInfo } from '../getProviderInfo'
import { mapStateToProps } from '../LocalProviderInformationContainer'

jest.mock('../getProviderInfo', () => ({
  getProviderInfo: jest.fn(() => ({ id: 'titelive', icon: 'logo-titeLive', name: 'Tite Live' })),
}))

describe('src | LocalProviderInformationContainer', () => {
  let state
  let props

  beforeEach(() => {
    state = {
      data: {
        offers: [
          {
            id: 'UU',
            name: 'Super Livre',
            isEvent: true,
            isThing: false,
            venueId: 'EFGH',
            productId: 'AGDK',
            thumbUrl: 'http://localhost/storage/thumbs/products/AERTR',
          },
        ],
      },
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      props = {
        offerId: 'UU',
        offererId: 'ABCD',
        providerName: 'fakeLocalProvider',
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(getProviderInfo).toHaveBeenCalledWith(props.providerName)
      expect(result).toStrictEqual({
        offererId: 'ABCD',
        offerName: 'Super Livre',
        providerInfo: { id: 'titelive', icon: 'logo-titeLive', name: 'Tite Live' },
        thumbUrl: 'http://localhost/storage/thumbs/products/AERTR',
        venueId: 'EFGH',
      })
    })
  })
})
