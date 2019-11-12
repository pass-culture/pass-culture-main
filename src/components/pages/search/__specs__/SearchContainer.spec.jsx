import { mapStateToProps, mapDispatchToProps } from '../SearchContainer'

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
          recommendations: [],
          types: [],
        },
      }
      const ownProps = {
        location: {
          search: '',
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        recommendations: [],
        types: [],
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
        const apiPath = 'Applaudir'

        // when
        mapDispatchToProps(dispatch, props).getRecommendations(apiPath)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: 'Applaudir',
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
          },
          type: 'REQUEST_DATA_GET_APPLAUDIR',
        })
      })
    })

    it('should decode apiPath', () => {
      // given
      const dispatch = jest.fn()
      const props = {}
      const apiPath = '%C3%89couter'
      // when
      mapDispatchToProps(dispatch, props).getRecommendations(apiPath)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: 'Écouter',
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
        },
        type: 'REQUEST_DATA_GET_ÉCOUTER',
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
