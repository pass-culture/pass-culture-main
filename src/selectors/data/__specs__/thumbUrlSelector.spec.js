import { selectThumbUrlByRouterMatch } from '../thumbUrlSelector'

jest.mock('../../../utils/thumb', () => ({
  DEFAULT_THUMB_URL: '/default/thumb/url',
}))

describe('selectThumbUrlByRouterMatch', () => {
  let booking
  let bookingId
  let mediation
  let mediationId
  let offer
  let offerId
  let stock
  let stockId
  const bookingThumbUrl = 'http://foo/mediations/AE'
  const productThumbUrl = 'http://foo/products/AE'
  const mediationThumbUrl = 'http://foo/mediations/AE'

  beforeEach(() => {
    bookingId = 'AB'
    mediationId = 'AE'
    offerId = 'AE'
    stockId = 'BV'
    mediation = {
      id: mediationId,
      thumbUrl: mediationThumbUrl,
    }
    booking = {
      id: bookingId,
      mediationId,
      stockId,
      thumbUrl: bookingThumbUrl,
    }
    offer = {
      id: offerId,
      product: {
        id: 'AE',
        thumbCount: 1,
        thumbUrl: productThumbUrl,
      },
      venue: {
        latitude: 42,
        longitude: 1.6,
      },
    }
    stock = {
      id: stockId,
      offerId,
    }
  })

  it('should return product thumbUrl when offerId in match and offer is without mediation and without booking', () => {
    // given
    offer.product.thumbCount = 0
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [],
        offers: [offer],
        stocks: [],
      },
    }
    const match = {
      params: {
        offerId,
      },
    }

    // when
    const result = selectThumbUrlByRouterMatch(state, match)

    // then
    expect(result).toBe(productThumbUrl)
  })

  it('should return mediation thumbUrl when bookingId in match and has mediation associated with', () => {
    // given
    const state = {
      data: {
        bookings: [booking],
        favorites: [],
        mediations: [mediation],
        offers: [offer],
        stocks: [stock],
      },
    }
    const match = {
      params: {
        bookingId,
      },
    }

    // when
    const result = selectThumbUrlByRouterMatch(state, match)

    // then
    expect(result).toBe(bookingThumbUrl)
  })

  it('should return mediation thumbUrl when offerId in match and offer', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [mediation],
        offers: [offer],
        stocks: [],
      },
    }
    const match = {
      params: {
        mediationId,
      },
    }

    // when
    const result = selectThumbUrlByRouterMatch(state, match)

    // then
    expect(result).toBe(mediationThumbUrl)
  })

  it('should return default thumb when no thumb are found', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [],
        offers: [],
        stocks: [],
      },
    }
    const match = {
      params: {},
    }

    // when
    const result = selectThumbUrlByRouterMatch(state, match)

    // then
    expect(result).toBe('/default/thumb/url')
  })
})
