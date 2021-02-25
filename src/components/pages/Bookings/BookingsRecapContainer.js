import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import BookingsRecap from './BookingsRecap'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default compose(withRouter, connect(mapStateToProps))(BookingsRecap)
