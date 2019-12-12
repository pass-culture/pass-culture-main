import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'
import { App } from './App'
import { isMaintenanceSelector } from '../selectors/isMaintenanceSelector'

export function mapStateToProps(state) {
  return {
    isMaintenanceActivated: isMaintenanceSelector(state),
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(App)
