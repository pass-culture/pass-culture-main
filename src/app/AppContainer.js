import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { selectCurrentUser, resolveCurrentUser } from 'store/selectors/data/usersSelectors'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'

import { App } from './App'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
    modalOpen: state.modal.isActive,
    isMaintenanceActivated: maintenanceSelector(state),
  }
}

export function mapDispatchToProps(dispatch) {
  return {
    getCurrentUser: ({ handleFail, handleSuccess }) => {
      dispatch(
        requestData({
          apiPath: '/users/current',
          resolve: resolveCurrentUser,
          handleFail,
          handleSuccess,
        })
      )
    },
  }
}

export default compose(withRouter, connect(mapStateToProps, mapDispatchToProps))(App)
