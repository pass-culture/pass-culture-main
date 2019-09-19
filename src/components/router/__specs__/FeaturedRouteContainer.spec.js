import { mapDispatchToProps, mapStateToProps } from '../FeaturedRouteContainer'

jest.mock('redux-thunk-data', () => {
  const actualModule = jest.requireActual('redux-thunk-data')
  const { requestData } = jest.requireActual('fetch-normalize-data')
  const mockRequestData = requestData
  return {
    ...actualModule,
    requestData: mockRequestData,
  }
})

describe('src | components | router | FeaturedRouteContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return areFeaturesLoaded and disabled', () => {
      // given
      const state = { data: { features: [{ isActive: false, nameKey: 'FOO' }] } }
      const ownProps = { featureName: 'FOO' }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        areFeaturesLoaded: true,
        isRouteDisabled: true,
      })
    })
  })

  describe('mapDispatchToProps()', () => {
    it('should dispatch toggleOverlay', () => {
      // given
      const dispatch = jest.fn()

      // when
      mapDispatchToProps(dispatch).requestGetFeatures()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/features',
          method: 'GET',
        },
        type: 'REQUEST_DATA_GET_/FEATURES',
      })
    })
  })
})
