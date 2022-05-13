import { App } from './App'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { loadFeatures } from 'store/features/thunks'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'
import { selectFeaturesInitialized } from 'store/features/selectors'
import { withRouter } from 'utils/withRouter'

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
