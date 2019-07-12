import { mapStateToProps } from '../OfferContainer'
import state from '../../../utils/mocks/state'

describe('src | components | pages | Offer | Offer | OfferContainer ', () => {
  let props

  beforeEach(() => {
    props = {
      match: {
        params: {
          offerId: 'UU',
        },
      },
      query: {
        translate: jest.fn(),
      },
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        formInitialValues: expect.any(Object),
        formOffererId: 'BA',
        formVenueId: 'DA',
        offer: {
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-03-07T10:39:23.560392Z',
          dateModifiedAtLastProvider: '2019-03-07T10:40:05.443621Z',
          id: 'UU',
          idAtProviders: null,
          isActive: true,
          isEvent: false,
          isThing: true,
          lastProviderId: null,
          mediationsIds: ['H4'],
          modelName: 'Offer',
          productId: 'LY',
          stocksIds: ['MU'],
          venueId: 'DA',
        },
        offerer: expect.any(Object),
        offerers: expect.any(Object),
        product: expect.any(Object),
        providers: [],
        selectedOfferType: expect.any(Object),
        stocks: expect.any(Object),
        types: expect.any(Object),
        url: 'https://ilestencoretemps.fr/',
        venue: expect.any(Object),
        venues: expect.any(Object),
      })
    })
  })
})
