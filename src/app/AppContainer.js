import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'
import { App } from './App'
import { maintenanceSelector } from '../selectors/maintenanceSelector'

export const mapStateToProps = state => {
  return {
    isMaintenanceActivated: maintenanceSelector(state),
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(App)
