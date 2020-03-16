import { mapStateToProps } from '../StocksManagerContainer'

describe('src | components | pages | Offer | StocksManagerContainer | mapStateToProps', () => {
  let state
  let props

  beforeEach(() => {
    state = {
      data: {
        offers: [{ id: 'A1', isEvent: true, isThing: false, productId: 'B1' }],
        providers: [],
        products: [{ id: 'B1', lastProviderId: 'C1' }],
        stocks: [{ offerId: 'A1' }],
      },
    }
    props = {
      offerId: 'A1',
      match: {},
    }
  })

  describe('mapStateToProps', () => {
    it('should return an empty object when offer was not found', () => {
      // given
      props.offerId = 'A2'

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({})
    })

    it('should return an object when offer was found', () => {
      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        isEvent: true,
        offer: {
          id: 'A1',
          isEvent: true,
          isThing: false,
          productId: 'B1',
        },
        product: {
          id: 'B1',
          lastProviderId: 'C1',
        },
        isCreationOfSecondStockPrevented: false,
        provider: undefined,
        stocks: [
          {
            offerId: 'A1',
          },
        ],
      })
    })

    describe('isCreationOfSecondStockPrevented', () => {
      it('should be false when offer is an event', () => {
        // given
        state.data.offers[0].isEvent = true
        state.data.offers[0].isThing = false

        // when
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('isCreationOfSecondStockPrevented', false)
      })

      it('should be false when stocks are equal to zero', () => {
        // given
        state.data.offers[0].isEvent = true
        state.data.offers[0].isThing = false
        state.data.stocks = []

        // when
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('isCreationOfSecondStockPrevented', false)
      })

      it('should be true when offer is a thing and stocks is superior to zero', () => {
        // given
        state.data.offers[0].isEvent = false
        state.data.offers[0].isThing = true

        // when
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('isCreationOfSecondStockPrevented', true)
      })
    })
  })
})
