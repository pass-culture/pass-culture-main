import { mapStateToProps, mapSizeToProps } from '../DeckContainer'

describe('src | components | pages | discovery | deck | DeckContainer', () => {
  let initialState
  let mediation
  let mediationId
  let offer
  let offerId
  let recommendation

  beforeEach(() => {
    mediationId = 1
    mediation = {
      frontText: null,
      id: mediationId,
      offerId,
    }
    offerId = 2
    offer = {
      id: offerId,
      isNotBookable: false,
      stocks: [{}],
      venue: {
        latitude: 48.91683,
        longitude: 2.4388,
      },
    }
    recommendation = {
      id: 'AE',
      mediationId,
      offerId,
      productIdentifier: 'product_0',
      uniqId: 3,
    }
    initialState = {
      data: {
        bookings: [],
        mediations: [mediation],
        offers: [offer],
        recommendations: [recommendation],
      },
      geolocation: {
        latitude: 41.1,
        longitude: 42.1,
      },
    }
  })

  describe('mapStateToProps', () => {
    describe('isFlipDisabled', () => {
      it('should be true when no currentRecommendation', () => {
        // given
        initialState = {
          data: {
            bookings: [],
            mediations: [],
            offers: [],
            recommendations: [],
          },
        }

        const props = {
          match: {
            params: {
              mediationId: 'RT',
              offerId: 'GHEZ',
            },
          },
        }

        // when
        const result = mapStateToProps(initialState, props)

        // then
        expect(result.isFlipDisabled).toBe(true)
      })
    })

    describe('nextLimit', () => {
      it('should return 0 when number of recommendations minus 1 is less than the number of remaining cards to trigger loading', () => {
        // given
        const props = {
          match: {
            params: {
              mediationId,
              offerId,
            },
          },
        }

        // when
        const result = mapStateToProps(initialState, props)

        // then
        expect(result.nextLimit).toBe(0)
      })
    })
  })

  describe('mapSizeToProps', () => {
    it('should return an object containing given height and width inferior to 500', () => {
      // given
      const dimensions = {
        height: 200,
        width: 100,
      }
      const expectedResult = { height: 200, width: 100 }

      // when
      const result = mapSizeToProps(dimensions)

      // then
      expect(result).toStrictEqual(expectedResult)
    })

    it('should return an object containing height and width equal to 500 when width > 500', () => {
      // given
      const dimensions = {
        height: 200,
        width: 800,
      }
      const expectedResult = { height: 200, width: 500 }

      // when
      const result = mapSizeToProps(dimensions)

      // then
      expect(result).toStrictEqual(expectedResult)
    })
  })
})
