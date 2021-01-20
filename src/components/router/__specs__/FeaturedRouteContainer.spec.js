import { mapDispatchToProps, mapStateToProps } from '../FeaturedRouteContainer'

jest.mock('../../../utils/fetch-normalize-data/requestData', () => {
  const { _requestData } = jest.requireActual(
    '../../../utils/fetch-normalize-data/reducers/data/actionCreators'
  )

  return {
    requestData: _requestData,
  }
})

describe('src | components | router | FeaturedRouteContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return the right props', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: false,
              nameKey: 'FOO',
            },
          ],
        },
        features: { fetchHasFailed: false },
      }
      const ownProps = { featureName: 'FOO' }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        areFeaturesLoaded: true,
        isRouteDisabled: true,
        featuresFetchFailed: false,
      })
    })
  })

  describe('mapDispatchToProps()', () => {
    it('should dispatch get features', () => {
      // given
      const dispatch = jest.fn()

      // when
      mapDispatchToProps(dispatch).requestGetFeatures()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/features',
          method: 'GET',
          handleFail: expect.any(Function),
        },
        type: 'REQUEST_DATA_GET_/FEATURES',
      })
    })
  })
})
