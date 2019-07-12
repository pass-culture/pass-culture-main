import { connect } from 'react-redux'

import SimpleLink from './SimpleLink'
import selectIsFeatureDisabled from '../router/selectIsFeatureDisabled'

export const mapStateToProps = (state, ownProps) => {
  const { disabledInMenu, disabledInMenuByFeatureName } = ownProps
  return {
    disabledInMenu:
      typeof disabledInMenu === "undefined"
        ? selectIsFeatureDisabled(state, disabledInMenuByFeatureName)
        : disabledInMenu
  }
}

export default connect(mapStateToProps)(SimpleLink)
