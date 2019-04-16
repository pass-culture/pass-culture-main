import { mapStateToProps, mapSizeToProps } from '../DeckContainer'

describe('src | components | pages | discovery | deck | DeckContainer', () => {
  let initialState

  beforeEach(() => {
    initialState = {
      card: {
        areDetailsVisible: false,
        draggable: true,
        isActive: false,
        unFlippable: false,
      },
      data: {
        bookings: [],
        recommendations: [
          {
            mediation: {
              firstThumbDominantColor: null,
              frontText: null,
              id: 1,
              offerId: 2,
              thumbCount: 0,
              tutoIndex: 'number',
            },
            mediationId: 1,
            offer: {
              id: 2,
              isFinished: false,
              stocks: [{}],
            },
            offerId: 2,
            uniqId: 3,
          },
        ],
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
              mediationId: 1,
              offerId: 2,
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
              mediationId: 1,
              offerId: 2,
            },
          },
        }
        initialState.data.recommendations[0].mediation.thumbCount = 0
        initialState.data.recommendations[0].mediation.tutoIndex = 1

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
              mediationId: 1,
              offerId: 2,
            },
          },
        }
        initialState.data.recommendations[0].mediation.thumbCount = 0
        initialState.data.recommendations[0].mediation.tutoIndex = null

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
              mediationId: 1,
              offerId: 2,
            },
          },
        }
        initialState.data.recommendations[0].mediation.thumbCount = 2
        initialState.data.recommendations[0].mediation.tutoIndex = 1

        // when
        const result = mapStateToProps(initialState, props)

        // then
        expect(result.isFlipDisabled).toBe(false)
      })
    })

    describe('nextLimit', () => {
      it('should return 0 when number of recommendations minus 1 is inferior the number of remaining cards to trigger loading', () => {
        // given
        const props = {
          match: {
            params: {
              mediationId: 1,
              offerId: 2,
            },
          },
        }
        initialState.data.recommendations[0].mediation.thumbCount = 2
        initialState.data.recommendations[0].mediation.tutoIndex = 1

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
      expect(result).toEqual(expectedResult)
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
      expect(result).toEqual(expectedResult)
    })
  })
})
