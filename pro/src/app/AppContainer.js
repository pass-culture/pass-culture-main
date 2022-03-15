import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { maintenanceSelector } from 'store/selectors/maintenanceSelector'

import { App } from './App'

export function mapStateToProps(state) {
  return {
    isMaintenanceActivated: maintenanceSelector(state),
  }
}

export default compose(withRouter, connect(mapStateToProps))(App)
