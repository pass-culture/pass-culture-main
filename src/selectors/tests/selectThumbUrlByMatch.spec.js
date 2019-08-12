import selectThumbUrlByRouterMatch from '../selectThumbUrlByRouterMatch'

describe('src | selectors | selectThumbUrlByRouterMatch', () => {
  let mediation
  let mediationId
  let offer
  let offerId
  const productThumbUrl = 'http://foo/products/AE'
  const mediationThumbUrl = 'http://foo/mediations/AE'
  beforeEach(() => {
    offerId = 'AE'
    offer = {
      id: offerId,
      product: {
        id: 'AE',
        thumbUrl: productThumbUrl,
      },
      venue: {
        latitude: 42,
        longitude: 1.6,
      },
    }
    mediationId = 'AE'
    mediation = {
      id: mediationId,
      thumbUrl: mediationThumbUrl,
    }
  })

  it('should return product thumbUrl when offerId in match and offer is without mediation', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [],
        offers: [offer],
        recommendations: [],
      },
    }
    const match = {
      params: {
        mediationId,
        offerId,
      },
    }

    // when
    const result = selectThumbUrlByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(productThumbUrl)
  })

  it('should return mediation thumbUrl when offerId in match and offer is with mediation', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [mediation],
        offers: [offer],
        recommendations: [],
      },
    }
    const match = {
      params: {
        mediationId,
        offerId,
      },
    }

    // when
    const result = selectThumbUrlByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(mediationThumbUrl)
  })
})
