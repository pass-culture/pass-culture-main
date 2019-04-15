import { selectCurrentUser } from 'with-login'

import selectUserOffererByOffererIdAndUserIdAndRightsType from 'selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'

function mapStateToProps(state, ownProps) {
  const { match } = ownProps
  const {
    params: { offererId },
  } = match
  const currentUser = selectCurrentUser(state)
  const { id: currentUserId } = currentUser || {}

  return {
    adminUserOfferer: selectUserOffererByOffererIdAndUserIdAndRightsType(
      state,
      offererId,
      currentUserId,
      'admin'
    ),
  }
}

export default mapStateToProps
