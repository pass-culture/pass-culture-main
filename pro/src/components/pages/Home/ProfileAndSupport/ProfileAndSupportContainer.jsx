import { connect } from 'react-redux'

import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import ProfileAndSupport from './ProfileAndSupport'

export function mapStateToProps(state) {
  return {
    user: selectCurrentUser(state),
  }
}

export default connect(mapStateToProps)(ProfileAndSupport)
