import { connect } from 'react-redux'
import { compose } from 'redux'

import { withRequiredLogin } from '../../hocs'
import Offerers from './Offerers'
import { closeNotification } from 'pass-culture-shared'
import {assignData} from 'redux-saga-data'


export const mapStateToProps = state => {
  return {
    pendingOfferers: state.data.pendingOfferers,
    offerers: state.data.offerers,
    notification: state.notification,
  }
}

export const mapDispatchToProps = (dispatch) => {
  return {
    assignData:() => dispatch(assignData({ offerers: [], pendingOfferers: [] })),

    closeNotification:() => dispatch(closeNotification()),
  }
}

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Offerers)
