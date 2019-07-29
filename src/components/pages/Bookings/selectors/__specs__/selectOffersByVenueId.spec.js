import selectOffersByVenueId from '../selectOffersByVenueId'

describe('src | components | pages | Bookings | selectors | selectOffersByVenueId', () => {
  it('should return an empty array when state contains no offers', () => {
    // given
    const venueId = 'CU'
    const state = {
      data: {
        offer: [],
      },
    }

    // when
    const result = selectOffersByVenueId(state, venueId)

    // then
    expect(result).toStrictEqual([])
  })

  it('should return an array of physical offers matching venueId', () => {
    // given
    const venueId = 'CU'
    const state = {
      data: {
        offers: [
          {
            id: 'A8HQ',
            venueId: 'CU',
          },
          {
            id: 'A8RQ',
            venueId: 'CU',
          },
          {
            id: 'AVGQ',
            venueId: 'B9',
          },
        ],
      },
    }

    // when
    const result = selectOffersByVenueId(state, venueId)

    // then
    expect(result).toStrictEqual([
      {
        id: 'A8HQ',
        venueId: 'CU',
      },
      {
        id: 'A8RQ',
        venueId: 'CU',
      },
    ])
  })
})
