import { connect } from 'react-redux'
import { compose } from 'redux'

import DiscoveryRouter from './DiscoveryRouter'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'

export const mapStateToProps = state => {
  const isDiscoveryV2Active = !selectIsFeatureDisabled(state, 'RECOMMENDATIONS_WITH_DISCOVERY_VIEW')

  return {
    isDiscoveryV2Active,
  }
}

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(DiscoveryRouter)
