import { mapDispatchToProps, mapStateToProps } from '../SearchContainer'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')

  return {
    requestData,
  }
})

describe('src | components | pages | SearchContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        data: {
          researchedRecommendations: [],
          types: [],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        researchedRecommendations: [],
        typeSublabels: [],
        typeSublabelsAndDescription: [],
        user: undefined,
      })
    })
  })

  describe('mapDispatchToProps', () => {
    describe('getRecommendations', () => {
      it('should request searched recommendations', () => {
        // given
        const dispatch = jest.fn()
        const props = {}
        const apiPath = '/recommendations?categories=Applaudir'

        // when
        mapDispatchToProps(dispatch, props).getResearchedRecommendations(apiPath)

        // then
        expect(dispatch.mock.calls[0][0]).toStrictEqual({
          config: {
            apiPath: '/recommendations?categories=Applaudir',
            handleSuccess: undefined,
            method: 'GET',
            normalizer: {
              bookings: {
                normalizer: {
                  stock: 'stocks',
                },
                stateKey: 'bookings',
              },
              mediation: 'mediations',
              offer: {
                normalizer: {
                  favorites: 'favorites',
                  stocks: 'stocks',
                },
                stateKey: 'offers',
              },
            },
            stateKey: 'researchedRecommendations',
          },
          type: 'REQUEST_DATA_GET_RESEARCHEDRECOMMENDATIONS',
        })
        expect(dispatch.mock.calls[1][0]).toStrictEqual({
          page: 1,
          type: 'UPDATE_PAGE',
        })
      })
    })

    it('should decode apiPath', () => {
      // given
      const dispatch = jest.fn()
      const props = {}
      const apiPath = '/recommendations?categories=%C3%89couter'
      // when
      mapDispatchToProps(dispatch, props).getResearchedRecommendations(apiPath)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/recommendations?categories=Écouter',
          handleSuccess: undefined,
          method: 'GET',
          normalizer: {
            bookings: {
              normalizer: {
                stock: 'stocks',
              },
              stateKey: 'bookings',
            },
            mediation: 'mediations',
            offer: {
              normalizer: {
                favorites: 'favorites',
                stocks: 'stocks',
              },
              stateKey: 'offers',
            },
          },
          stateKey: 'researchedRecommendations',
        },
        type: 'REQUEST_DATA_GET_RESEARCHEDRECOMMENDATIONS',
      })
    })

    describe('getTypes', () => {
      it('should request types', () => {
        // given
        const dispatch = jest.fn()
        const props = {}

        // when
        mapDispatchToProps(dispatch, props).getTypes()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/types',
            method: 'GET',
          },
          type: 'REQUEST_DATA_GET_/TYPES',
        })
      })
    })
  })
})
