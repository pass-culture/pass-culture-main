import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import FeaturedRoute from './FeaturedRoute'
import selectIsFeatureDisabled from './selectIsFeatureDisabled'

const mapStateToProps = (state, ownProps) => {
  const { features } = state.data
  const { featureName } = ownProps
  return {
    features,
    isFeatureDisabled: selectIsFeatureDisabled(state, featureName),
  }
}

const mapDispatchToProps = dispatch => ({
  requestGetFeatures: () => dispatch(requestData({ apiPath: '/features' })),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(FeaturedRoute)
