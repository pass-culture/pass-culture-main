import { connect } from 'react-redux'

import MenuItem from './MenuItem'
import selectIsFeatureDisabled from '../router/selectors/selectIsFeatureDisabled'

export const mapStateToProps = (state, ownProps) => {
  const { item } = ownProps
  const { featureName } = item
  const disabled = featureName ? selectIsFeatureDisabled(state, featureName) : false
  return {
    disabled,
  }
}

export default connect(mapStateToProps)(MenuItem)
