import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'
import { App } from './App'

function mapStateToProps(state) {
  return {
    modalOpen: state.modal.isActive,
    isMaintenanceActivated: false,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(App)
