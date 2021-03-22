import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import { selectIsFeatureActive } from '../../../store/selectors/data/featuresSelectors'

import HeaderSwitch from './HeaderSwitch'

export const mapStateToProps = state => {
  const { data } = state
  const user = selectCurrentUser(state)
  const { publicName: name, isAdmin: isUserAdmin } = user
  const { offerers } = data

  return {
    isNewHomepageActive: selectIsFeatureActive(state, 'PRO_HOMEPAGE'),
    isUserAdmin,
    name,
    offerers,
  }
}

export default compose(withRouter, connect(mapStateToProps))(HeaderSwitch)
