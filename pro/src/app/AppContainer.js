/*
 * @debt deprecated "Gaël: deprecated usage of redux-saga-data"
 * @debt standard "Gaël: prefer hooks for routers (https://reactrouter.com/web/api/Hooks)"
 * @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
 */

import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { selectFeaturesInitialized } from 'store/features/selectors'
import { loadFeatures } from 'store/features/thunks'
import {
  selectCurrentUser,
  resolveCurrentUser,
} from 'store/selectors/data/usersSelectors'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'

import { App } from './App'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
    isMaintenanceActivated: maintenanceSelector(state),
    isFeaturesInitialized: selectFeaturesInitialized(state),
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
    loadFeatures: () => {
      dispatch(loadFeatures())
    },
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps, mapDispatchToProps)
)(App)
