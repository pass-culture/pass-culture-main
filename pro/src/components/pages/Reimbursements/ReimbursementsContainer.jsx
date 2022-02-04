import { connect } from 'react-redux'

import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import ReimbursementsWithFilters from './ReimbursementsWithFilters'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default connect(mapStateToProps)(ReimbursementsWithFilters)
