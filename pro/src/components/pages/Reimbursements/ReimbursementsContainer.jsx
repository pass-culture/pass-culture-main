/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import React from 'react'
import { connect } from 'react-redux'

import useActiveFeature from 'components/hooks/useActiveFeature'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import Reimbursements from './Reimbursements'
import ReimbursementsWithFilters from './ReimbursementsWithFilters'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

const ReimbursementsWithActiveFeature = props =>
  useActiveFeature('PRO_REIMBURSEMENTS_FILTERS') ? (
    <ReimbursementsWithFilters {...props} />
  ) : (
    <Reimbursements {...props} />
  )

export default connect(mapStateToProps)(ReimbursementsWithActiveFeature)
