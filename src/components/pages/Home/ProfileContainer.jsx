import { connect } from 'react-redux'

import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import Profile from './Profile'

export function mapStateToProps(state) {
  return {
    user: selectCurrentUser(state),
  }
}

export default connect(mapStateToProps)(Profile)
