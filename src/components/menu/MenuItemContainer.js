import { connect } from 'react-redux'

import MenuItem from './MenuItem'
import selectIsFeatureDisabled from '../router/selectIsFeatureDisabled'

export const mapStateToProps = (state, ownProps) => {
  const { item } = ownProps
  const { featureName } = item
  return {
    disabled: selectIsFeatureDisabled(state, featureName),
  }
}

export default connect(mapStateToProps)(MenuItem)
