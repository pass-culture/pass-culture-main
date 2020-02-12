import { mapStateToProps } from '../StocksManagerContainer'

describe('components | OfferEdition | StocksManagerContainer', () => {
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
      match: {},
    }
  })

  describe('mapStateToProps', () => {
    it('should return an empty object when offer was not found', () => {
      // given
      props.match.params = {
        offerId: 'A2',
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({})
    })

    it('should return an object when offer was found', () => {
      // given
      props.match.params = {
        offerId: 'A1',
      }

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
        creationOfSecondStockIsPrevented: false,
        provider: undefined,
        stocks: [
          {
            offerId: 'A1',
          },
        ],
      })
    })

    describe('creationOfSecondStockIsPrevented', () => {
      it('should be false when offer is an event', () => {
        // given
        state.data.offers[0].isEvent = true
        state.data.offers[0].isThing = false
        props.match.params = {
          offerId: 'A1',
        }

        // when
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('creationOfSecondStockIsPrevented', false)
      })

      it('should be false when stocks are equal to zero', () => {
        // given
        state.data.offers[0].isEvent = true
        state.data.offers[0].isThing = false
        state.data.stocks = []
        props.match.params = {
          offerId: 'A1',
        }

        // when
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('creationOfSecondStockIsPrevented', false)
      })

      it('should be true when offer is a thing and stocks is superior to zero', () => {
        // given
        state.data.offers[0].isEvent = false
        state.data.offers[0].isThing = true
        props.match.params = {
          offerId: 'A1',
        }

        // when
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('creationOfSecondStockIsPrevented', true)
      })
    })
  })
})
