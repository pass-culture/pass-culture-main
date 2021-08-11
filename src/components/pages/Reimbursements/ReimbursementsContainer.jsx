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
