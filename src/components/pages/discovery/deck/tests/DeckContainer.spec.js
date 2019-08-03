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
      firstThumbDominantColor: null,
      frontText: null,
      id: mediationId,
      offerId,
      thumbCount: 0,
      tutoIndex: 'number',
    }
    offerId = 2
    offer =  {
      id: offerId,
      isFinished: false,
      stocks: [{}],
      venue: {
        latitude: 48.91683,
        longitude: 2.4388,
      },
    }
    recommendation = {
      discoveryIdentifier: 'product_0',
      id: "AE",
      mediationId,
      offerId,
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
      it('should be false when currentRecommendation and no mediation', () => {
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
        expect(result.isFlipDisabled).toBe(false)
      })

      it('should be true when no currentRecommendation and tutoIndex is a number and thumbCount <= 1', () => {
        // given
        const props = {
          match: {
            params: {
              mediationId,
              offerId,
            },
          },
        }
        initialState.data.mediations[0].thumbCount = 0
        initialState.data.mediations[0].tutoIndex = 1

        // when
        const result = mapStateToProps(initialState, props)

        // then
        expect(result.isFlipDisabled).toBe(true)
      })

      it('should be false when no currentRecommendation and tutoIndex not a number', () => {
        // given
        const props = {
          match: {
            params: {
              mediationId,
              offerId,
            },
          },
        }
        initialState.data.mediations[0].thumbCount = 0
        initialState.data.mediations[0].tutoIndex = null

        // when
        const result = mapStateToProps(initialState, props)

        // then
        expect(result.isFlipDisabled).toBe(false)
      })

      it('should be false when no currentRecommendation and thumbCount > 1', () => {
        // given
        const props = {
          match: {
            params: {
              mediationId,
              offerId,
            },
          },
        }
        initialState.data.mediations[0].thumbCount = 2
        initialState.data.mediations[0].tutoIndex = 1

        // when
        const result = mapStateToProps(initialState, props)

        // then
        expect(result.isFlipDisabled).toBe(false)
      })
    })

    describe('nextLimit', () => {
      it('should return 1 (because of the fake last reco) when number of recommendations minus 1 is inferior the number of remaining cards to trigger loading', () => {
        // given
        const props = {
          match: {
            params: {
              mediationId,
              offerId,
            },
          },
        }
        initialState.data.mediations[0].thumbCount = 2
        initialState.data.mediations[0].tutoIndex = 1

        // when
        const result = mapStateToProps(initialState, props)

        // then
        expect(result.nextLimit).toBe(1)
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
