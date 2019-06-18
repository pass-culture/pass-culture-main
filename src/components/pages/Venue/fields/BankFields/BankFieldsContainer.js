import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectCurrentUser } from 'with-login'

import BankFields from './BankFields'
import withFrenchQueryRouter from '../../../../hocs/withFrenchQueryRouter'
import selectUserOffererByOffererIdAndUserIdAndRightsType from '../../../../../selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const {
    params: { offererId },
  } = match
  const currentUser = selectCurrentUser(state)
  const { id: currentUserId } = currentUser || {}

  const adminUserOfferer = selectUserOffererByOffererIdAndUserIdAndRightsType(
    state,
    offererId,
    currentUserId,
    'admin'
  )

  return {
    adminUserOfferer: adminUserOfferer,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(BankFields)
