import { connect } from 'react-redux'

import MenuItem from './MenuItem'
import selectIsFeatureDisabled from '../../../router/selectors/selectIsFeatureDisabled'

export const mapStateToProps = (state, ownProps) => {
  const { item } = ownProps
  const { featureName } = item
  const isFeatureFlipped = featureName !== undefined
  const isDisabled = !isFeatureFlipped ? false : selectIsFeatureDisabled(state, featureName)

  return {
    isDisabled,
  }
}

export default connect(mapStateToProps)(MenuItem)
