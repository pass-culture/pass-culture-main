import { mapStateToProps } from '../CancelThisLinkContainer'

describe('src | components | verso | verso-controls | booking | CancelThisLinkContainer', () => {
  it('returns an object containing props', () => {
    // given
    const state = {}
    const props = {
      booking: {
        isCancelled: false,
        stock: {
          price: 1,
        },
      },
      history: {},
    }

    // when
    const result = mapStateToProps(state, props)

    // then
    const expected = {
      history: {},
      isCancelled: false,
      priceValue: 1,
    }
    expect(result).toStrictEqual(expected)
  })
})
