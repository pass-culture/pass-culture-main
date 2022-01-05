/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 * @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
 */

import { connect } from 'react-redux'

import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import ReimbursementsWithFilters from './ReimbursementsWithFilters'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default connect(mapStateToProps)(ReimbursementsWithFilters)
