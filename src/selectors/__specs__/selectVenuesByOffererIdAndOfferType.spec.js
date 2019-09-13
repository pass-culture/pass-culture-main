import selectVenuesByOffererIdAndOfferType from '../selectVenuesByOffererIdAndOfferType'

describe('src | selectors | selectVenuesByOffererIdAndOfferType', () => {
  it('should return an empty array when state contains no venues', () => {
    // given
    const state = {
      data: {
        venues: [],
      },
    }

    // when
    const result = selectVenuesByOffererIdAndOfferType(state)

    // then
    expect(result).toStrictEqual([])
  })

  it('should return array of object when state contains on venue that is virtual', () => {
    // given
    const state = {
      data: {
        venues: [
          {
            isVirtual: true,
          },
        ],
      },
    }

    // when
    const expected = [
      {
        isVirtual: true,
      },
    ]
    const result = selectVenuesByOffererIdAndOfferType(state)

    // then
    expect(result).toStrictEqual(expected)
  })
})
