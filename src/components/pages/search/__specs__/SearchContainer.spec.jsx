import { mapDispatchToProps, mapStateToProps } from '../SearchContainer'

jest.mock('redux-thunk-data', () => {
  const { assignData, requestData } = jest.requireActual('fetch-normalize-data')

  return {
    requestData,
    assignData,
  }
})

describe('src | components | pages | SearchContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        data: {
          searchedRecommendations: [],
          types: [],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        searchedRecommendations: [],
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
        mapDispatchToProps(dispatch, props).getSearchedRecommendations(apiPath)

        // then
        const firstDispatchedAction = dispatch.mock.calls[0][0]
        const secondDispatchedAction = dispatch.mock.calls[1][0]
        expect(firstDispatchedAction).toStrictEqual({
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
            stateKey: 'searchedRecommendations',
          },
          type: 'REQUEST_DATA_GET_SEARCHEDRECOMMENDATIONS',
        })
        expect(secondDispatchedAction).toStrictEqual({
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
      mapDispatchToProps(dispatch, props).getSearchedRecommendations(apiPath)

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
          stateKey: 'searchedRecommendations',
        },
        type: 'REQUEST_DATA_GET_SEARCHEDRECOMMENDATIONS',
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

    describe('resetSearchedRecommendations', () => {
      it('should reset searched recommendations', () => {
        // given
        const dispatch = jest.fn()
        const props = {}

        // when
        mapDispatchToProps(dispatch, props).resetSearchedRecommendations()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          patch: {
            searchedRecommendations: [],
          },
          type: 'ASSIGN_DATA',
        })
      })
    })
  })
})
