import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'

import FeaturedRoute from './FeaturedRoute'
import selectIsFeatureDisabled from './selectors/selectIsFeatureDisabled'

export const mapStateToProps = (state, ownProps) => {
  const { features } = state.data
  const { featureName } = ownProps

  let isRouteDisabled
  if (!featureName) {
    isRouteDisabled = false
  } else {
    isRouteDisabled = selectIsFeatureDisabled(state, featureName)
  }

  return {
    areFeaturesLoaded: features.length > 0,
    isRouteDisabled,
  }
}

export const mapDispatchToProps = dispatch => ({
  requestGetFeatures: () => dispatch(requestData({ apiPath: '/features' })),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(FeaturedRoute)
