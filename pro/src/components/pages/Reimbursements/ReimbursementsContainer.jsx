import ReimbursementsWithFilters from './ReimbursementsWithFilters'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'store/user/selectors'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default connect(mapStateToProps)(ReimbursementsWithFilters)
