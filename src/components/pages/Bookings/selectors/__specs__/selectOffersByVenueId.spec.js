import selectOffersByVenueId from '../selectOffersByVenueId'

describe('src | components | pages | Bookings | selectors | selectOffersByVenueId', () => {
  it('should return an empty list of offers when state contains no offers', () => {
    // given
    const venueId = 'CU'
    const state = {
      data: {
        offer: [],
      },
    }

    // when
    const offersToDisplay = selectOffersByVenueId(state, venueId)

    // then
    expect(offersToDisplay).toStrictEqual([])
  })

  it('should return only the offers from to a specific venue', () => {
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
    const offersToDisplay = selectOffersByVenueId(state, venueId)

    // then
    const offersListExpected = [
      {
        id: 'A8HQ',
        venueId: 'CU',
      },
      {
        id: 'A8RQ',
        venueId: 'CU',
      },
    ]

    expect(offersToDisplay).toStrictEqual(offersListExpected)
  })

  it('should return an empty list of offers when state is not initialized', () => {
    // given
    const venueId = 'CU'
    const state = {
      data: {},
    }

    // when
    const offersToDisplay = selectOffersByVenueId(state, venueId)

    // then
    const offersListExpected = []
    expect(offersToDisplay).toStrictEqual(offersListExpected)
  })
})
