import selectNonVirtualVenues from '../selectNonVirtualVenues'

describe('src | components | pages | Bookings | selectors | selectNonVirtualVenues', () => {
  it('should return an empty list of non virtual venues when state contains no venues', () => {
    // given
    const state = {
      data: {
        venues: [],
      },
    }

    // when
    const nonVirtualVenuesToDisplay = selectNonVirtualVenues(state)

    // then
    expect(nonVirtualVenuesToDisplay).toStrictEqual([])
  })

  it('should return only the non virtual venues', () => {
    // given
    const state = {
      data: {
        venues: [
          {
            id: 'A8HQ',
            isVirtual: true,
          },
          {
            id: 'A8RQ',
            isVirtual: false,
          },
          {
            id: 'AVGQ',
            isVirtual: false,
          },
        ],
      },
    }

    // when
    const nonVirtualVenuesToDisplay = selectNonVirtualVenues(state)

    // then
    const nonVirtualVenuesListExpected = [
      {
        id: 'A8RQ',
        isVirtual: false,
      },
      {
        id: 'AVGQ',
        isVirtual: false,
      },
    ]

    expect(nonVirtualVenuesToDisplay).toStrictEqual(nonVirtualVenuesListExpected)
  })

  it('should return an empty list of offer when state is not initialized', () => {
    // given
    const state = {
      data: {},
    }

    // when
    const nonVirtualVenuesToDisplay = selectNonVirtualVenues(state)

    // then
    const nonVirtualVenuesListExpected = []
    expect(nonVirtualVenuesToDisplay).toStrictEqual(nonVirtualVenuesListExpected)
  })
})
