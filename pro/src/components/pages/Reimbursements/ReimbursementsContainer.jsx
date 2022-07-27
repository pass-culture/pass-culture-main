import { connect } from 'react-redux'

import { selectCurrentUser } from 'store/user/selectors'

import ReimbursementsWithFilters from './ReimbursementsWithFilters'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default connect(mapStateToProps)(ReimbursementsWithFilters)
