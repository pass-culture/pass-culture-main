import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import getIsConfirmingCancelling from '../../../helpers/getIsConfirmingCancelling'
import Details from './Details'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const isConfirmingCancelling = getIsConfirmingCancelling(match)

  return {
    isConfirmingCancelling,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Details)
