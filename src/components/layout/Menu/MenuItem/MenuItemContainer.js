import { connect } from 'react-redux'

import MenuItem from './MenuItem'
import selectIsFeatureDisabled from '../../../router/selectors/selectIsFeatureDisabled'

export const mapStateToProps = (state, ownProps) => {
  const { item } = ownProps
  const { featureName } = item

  const isFeatureFlipped = item.hasOwnProperty('featureName')

  let disabled
  if (!isFeatureFlipped) {
    disabled = false
  } else {
    disabled = selectIsFeatureDisabled(state, featureName)
  }

  return {
    disabled,
  }
}

export default connect(mapStateToProps)(MenuItem)
