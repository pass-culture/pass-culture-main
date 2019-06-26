import selectNonVirtualVenues from '../selectNonVirtualVenues'

describe('src | components | pages | Bookings | selectNonVirtualVenues', () => {
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
    expect(nonVirtualVenuesToDisplay).toEqual([])
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

    expect(nonVirtualVenuesToDisplay).toEqual(nonVirtualVenuesListExpected)
  })

  it('should return an empty list of offer when state is not initialized', () => {
    // given
    const state = {}

    // when
    const nonVirtualVenuesToDisplay = selectNonVirtualVenues(state)

    // then
    const nonVirtualVenuesListExpected = []

    expect(nonVirtualVenuesToDisplay).toEqual(nonVirtualVenuesListExpected)
  })
})
