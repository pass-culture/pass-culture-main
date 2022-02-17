import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import OffererDetails from './OffererDetails'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const {
    params: { offererId },
  } = match
  const currentUser = selectCurrentUser(state)
  return {
    currentUser,
    offererId,
  }
}

export default compose(withRouter, connect(mapStateToProps))(OffererDetails)
