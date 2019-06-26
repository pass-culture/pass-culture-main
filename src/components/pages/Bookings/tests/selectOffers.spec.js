import selectOffers from '../selectOffers'

describe('src | components | pages | Bookings | selectOffers', () => {
  it('should return an empty list of offers when state contains no offer', () => {
    // given
    const onlineOnly = true
    const state = {
      data: {
        offers: [],
      },
    }

    // when
    const offersToDisplay = selectOffers(onlineOnly, state)

    // then
    expect(offersToDisplay).toEqual([])
  })

  it('should return only digital offers when user checks the box to see only digital offer', () => {
    // given
    const onlineOnly = true
    const state = {
      data: {
        offers: [
          {
            id: 'AVJA',
            product: {
              offerType: {
                onlineOnly: true,
              },
            },
          },
          {
            id: 'AVHA',
            product: {
              offerType: {
                onlineOnly: true,
              },
            },
          },
          {
            id: 'AVFA',
            product: {
              offerType: {
                onlineOnly: false,
              },
            },
          },
        ],
      },
    }

    // when
    const offersToDisplay = selectOffers(onlineOnly, state)

    // then
    const offerListExpected = [
      {
        id: 'AVJA',
        product: {
          offerType: {
            onlineOnly: true,
          },
        },
      },
      {
        id: 'AVHA',
        product: {
          offerType: {
            onlineOnly: true,
          },
        },
      },
    ]

    expect(offersToDisplay).toEqual(offerListExpected)
  })

  it('should return only non digital offers when user unchecks the box to see only digital offer', () => {
    // given
    const onlineOnly = false
    const state = {
      data: {
        offers: [
          {
            id: 'AVJA',
            product: {
              offerType: {
                onlineOnly: true,
              },
            },
          },
          {
            id: 'AVHA',
            product: {
              offerType: {
                onlineOnly: true,
              },
            },
          },
          {
            id: 'AVFA',
            product: {
              offerType: {
                onlineOnly: false,
              },
            },
          },
        ],
      },
    }

    // when
    const offersToDisplay = selectOffers(onlineOnly, state)

    // then
    const offerListExpected = [
      {
        id: 'AVFA',
        product: {
          offerType: {
            onlineOnly: false,
          },
        },
      },
    ]

    expect(offersToDisplay).toEqual(offerListExpected)
  })

  it('should return an empty list of offer when state is not initialized', () => {
    // given
    const onlineOnly = true
    const state = {}

    // when
    const offersToDisplay = selectOffers(onlineOnly, state)

    // then
    const offerListExpected = []

    expect(offersToDisplay).toEqual(offerListExpected)
  })
})
