import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'
import { App } from './App'
import { maintenanceSelector } from '../../redux/selectors/maintenanceSelector'
import { selectCurrentUser } from '../../redux/selectors/currentUserSelector'

export const mapStateToProps = state => {
  const isUserConnected = selectCurrentUser(state) != null

  return {
    isMaintenanceActivated: maintenanceSelector(state),
    isUserConnected,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(App)
