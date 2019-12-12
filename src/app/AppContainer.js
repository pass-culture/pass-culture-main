import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'
import { App } from './App'

function mapStateToProps(state) {
  return {
    isMaintenanceActivated: true,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(App)
