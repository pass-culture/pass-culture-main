/*
 * @debt standard "Gaël: prefer hooks for routers (https://reactrouter.com/web/api/Hooks)"
 * @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
 */

import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { selectFeaturesInitialized } from 'store/features/selectors'
import { loadFeatures } from 'store/features/thunks'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'
import { selectUserInitialized } from 'store/user/selectors'
import { loadUser } from 'store/user/thunks'

import { App } from './App'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
    isUserInitialized: selectUserInitialized(state),
    isMaintenanceActivated: maintenanceSelector(state),
    isFeaturesInitialized: selectFeaturesInitialized(state),
  }
}

export function mapDispatchToProps(dispatch) {
  return {
    getCurrentUser: () => {
      dispatch(loadUser())
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
