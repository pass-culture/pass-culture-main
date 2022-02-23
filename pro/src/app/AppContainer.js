import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { selectFeaturesInitialized } from 'store/features/selectors'
import { loadFeatures } from 'store/features/thunks'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'

import { App } from './App'

export function mapStateToProps(state) {
  return {
    isMaintenanceActivated: maintenanceSelector(state),
    isFeaturesInitialized: selectFeaturesInitialized(state),
  }
}

export function mapDispatchToProps(dispatch) {
  return {
    loadFeatures: () => {
      dispatch(loadFeatures())
    },
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps, mapDispatchToProps)
)(App)
