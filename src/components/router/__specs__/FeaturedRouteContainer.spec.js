import { mapDispatchToProps, mapStateToProps } from '../FeaturedRouteContainer'

jest.mock('../../../utils/fetch-normalize-data/requestData', () => {
  const { _requestData } = jest.requireActual('../../../utils/fetch-normalize-data/reducers/data/actionCreators')

  return {
    requestData: _requestData,
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
