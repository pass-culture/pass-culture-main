import selectDistanceByOfferId from '../selectDistanceByOfferId'

describe('src | selectors | selectDistanceByOfferId', () => {
  let offer
  let offerId
  beforeEach(() => {
    offerId = 'AE'
    offer = {
      id: offerId,
      venue: {
        latitude: 42,
        longitude: 1.6,
      },
    }
  })

  it('should return distance from offerId', () => {
    // given
    const state = {
      data: {
        offers: [offer],
      },
      geolocation: {
        latitude: 42.5,
        longitude: 1.7,
      },
    }

    // when
    const result = selectDistanceByOfferId(state, offerId)

    // then
    expect(result).toStrictEqual('56 km')
  })
})
