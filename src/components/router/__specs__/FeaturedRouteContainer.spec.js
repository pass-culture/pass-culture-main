import { mapDispatchToProps, mapStateToProps } from '../FeaturedRouteContainer'

describe('src | components | router | FeaturedRouteContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return areFeaturesLoaded falsy when state contain no feature', () => {
      // given
      const state = {
        data: {
          features: []
        }
      }
      const ownProps = { featureName: 'FOO' }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        areFeaturesLoaded: false,
        isRouteDisabled: true,
      })
    })

    it('should return areFeaturesLoaded and disabled when feature isActive is set to false', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: false,
              nameKey: 'FOO'
            }]
        }
      }
      const ownProps = { featureName: 'FOO' }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        areFeaturesLoaded: true,
        isRouteDisabled: true,
      })
    })

    it('should return areFeaturesLoaded truthy and disabled falsy when feature isActive is set to true', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: true,
              nameKey: 'FOO'
            }]
        }
      }
      const ownProps = { featureName: 'FOO' }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        areFeaturesLoaded: true,
        isRouteDisabled: false,
      })
    })

    it('should return areFeaturesLoaded and disabled when no props are given', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: true,
              nameKey: 'FOO'
            }]
        }
      }
      const ownProps = {}

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        areFeaturesLoaded: true,
        isRouteDisabled: false,
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
