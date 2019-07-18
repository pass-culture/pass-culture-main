import selectOffers from '../selectOffers'

describe('src | components | pages | Bookings | selectors | selectOffers', () => {
  it('should return an empty list of digital offers when state contains no offers', () => {
    // given
    const state = {
      data: {
        offer: [],
      },
    }

    // when
    const digitalOffersToDisplay = selectOffers(state)

    // then
    expect(digitalOffersToDisplay).toStrictEqual([])
  })

  it('should return only the digital offers when isDigital is selected', () => {
    // given
    const isDigital = true
    const state = {
      data: {
        offers: [
          {
            id: 'A8HQ',
            isDigital: true,
          },
          {
            id: 'A8RQ',
            isDigital: false,
          },
          {
            id: 'AVGQ',
            isDigital: false,
          },
        ],
      },
    }

    // when
    const digitalOffersToDisplay = selectOffers(state, isDigital)

    // then
    const digitalOffersListExpected = [
      {
        id: 'A8HQ',
        isDigital: true,
      },
    ]

    expect(digitalOffersToDisplay).toStrictEqual(digitalOffersListExpected)
  })

  it('should return only the non digital offers when filtering out online only', () => {
    // given
    const isDigital = false
    const state = {
      data: {
        offers: [
          {
            id: 'A8HQ',
            isDigital: true,
          },
          {
            id: 'A8RQ',
            isDigital: false,
          },
          {
            id: 'AVGQ',
            isDigital: false,
          },
        ],
      },
    }

    // when
    const digitalOffersToDisplay = selectOffers(state, isDigital)

    // then
    const digitalOffersListExpected = [
      {
        id: 'A8RQ',
        isDigital: false,
      },
      {
        id: 'AVGQ',
        isDigital: false,
      },
    ]

    expect(digitalOffersToDisplay).toStrictEqual(digitalOffersListExpected)
  })

  it('should return an empty list of digital offers when state is not initialized', () => {
    // given
    const state = {
      data: {},
    }

    // when
    const digitalOffersToDisplay = selectOffers(state)

    // then
    const digitalOffersListExpected = []
    expect(digitalOffersToDisplay).toStrictEqual(digitalOffersListExpected)
  })
})
