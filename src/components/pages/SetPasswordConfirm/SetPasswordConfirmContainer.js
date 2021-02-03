import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import { SetPasswordConfirm } from './SetPasswordConfirm'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default compose(connect(mapStateToProps))(withRouter(SetPasswordConfirm))
