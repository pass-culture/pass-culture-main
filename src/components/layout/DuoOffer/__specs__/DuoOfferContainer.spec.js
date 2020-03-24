import { mapStateToProps } from '../DuoOfferContainer'

describe('src | components | layout | DuoOffer | DuoOfferContainer', () => {
  let ownProps
  let state

  beforeEach(() => {
    ownProps = {
      offerId: 'AAAA',
    }

    state = {
      data: {
        offers: [
          {
            id: 'AAAA',
            isDuo: true,
            stockId: 'ABCD',
          },
        ],
        stocks: [
          {
            remainingQuantityOrUnlimited: 2,
            id: 'ABCD',
            offerId: 'AAAA',
          },
        ],
      },
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object with isDisabled to true when stock is more than 2 and is on duo offer', () => {
      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isDuoOffer: true,
      })
    })

    it('should return an object with isDisabled to false when stock is less than 2', () => {
      // given
      state.data.stocks = [
        {
          remainingQuantityOrUnlimited: 1,
          id: 'ABCD',
          offerId: 'AAAA',
        },
      ]

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isDuoOffer: false,
      })
    })

    it('should return an object with isDisabled to false when offer is not Duo', () => {
      // given
      state.data.offers = [
        {
          id: 'AAAA',
          isDuo: false,
          stockId: 'ABCD',
        },
      ]

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isDuoOffer: false,
      })
    })
  })
})
