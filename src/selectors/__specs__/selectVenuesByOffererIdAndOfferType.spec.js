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

  it('should return an array of object when state contains virtual venue', () => {
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
    const result = selectVenuesByOffererIdAndOfferType(state)

    // then
    const expected = [
      {
        isVirtual: true,
      },
    ]
    expect(result).toStrictEqual(expected)
  })
})
