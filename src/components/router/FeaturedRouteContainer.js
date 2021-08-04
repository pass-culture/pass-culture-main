import { connect } from 'react-redux'

import { requestData } from '../../utils/fetch-normalize-data/requestData'
import FeaturedRoute from './FeaturedRoute'
import selectIsFeatureDisabled from './selectors/selectIsFeatureDisabled'
import { featuresFetchFailed } from '../../redux/actions/features'

export const mapStateToProps = (state, ownProps) => {
  const { features } = state.data
  const { featureName } = ownProps
  const featuresFetchFailed = state.features.fetchHasFailed
  const isFeatureFlipped = featureName !== undefined
  const isRouteDisabled = !isFeatureFlipped ? false : selectIsFeatureDisabled(state, featureName)

  return {
    areFeaturesLoaded: features.length > 0,
    isRouteDisabled,
    featuresFetchFailed,
  }
}

export const handleFeaturesFetchFailed = dispatch => () => {
  dispatch(featuresFetchFailed())
}

export const mapDispatchToProps = dispatch => ({
  requestGetFeatures: () =>
    dispatch(
      requestData({ apiPath: '/features', handleFail: handleFeaturesFetchFailed(dispatch) })
    ),
  handleRequestCategories: () => {
    dispatch(
      requestData({
        apiPath: '/offers/categories',
        stateKey: 'categories',
      })
    )
  },
})

export default connect(mapStateToProps, mapDispatchToProps)(FeaturedRoute)
