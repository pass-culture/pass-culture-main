import selectDigitalOffers from '../selectDigitalOffers'

describe('src | components | pages | Bookings | selectors | selectDigitalOffers', () => {
  it('should return an empty array when state contains no offers', () => {
    // given
    const state = {
      data: {
        offers: [],
      },
    }

    // when
    const result = selectDigitalOffers(state)

    // then
    expect(result).toStrictEqual([])
  })

  it('should return an array containing only digital offers', () => {
    // given
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
    const result = selectDigitalOffers(state)

    // then
    expect(result).toStrictEqual([
      {
        id: 'A8HQ',
        isDigital: true,
      },
    ])
  })
})
