import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import { STYLEGUIDE_ACTIVE } from './_constants'
import Header from './Header'

export const mapStateToProps = state => {
  const user = selectCurrentUser(state)
  return {
    isUserAdmin: user && user.isAdmin,
    isStyleguideActive: STYLEGUIDE_ACTIVE,
  }
}

export default compose(withRouter, connect(mapStateToProps))(Header)
