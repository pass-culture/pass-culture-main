import Desk from './Desk'
import { compose } from 'redux'
import { connect } from 'react-redux'

import { withRequiredLogin } from '../../hocs'

export const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    validateBooking: (code) => {

    }
  }
}

export default compose(
  withRequiredLogin,
  connect(
    null,
    mapDispatchToProps
  )
)(Desk)
