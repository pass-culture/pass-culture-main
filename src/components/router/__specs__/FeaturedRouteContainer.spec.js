import { mapDispatchToProps, mapStateToProps } from '../FeaturedRouteContainer'

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
        disabled: true,
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
