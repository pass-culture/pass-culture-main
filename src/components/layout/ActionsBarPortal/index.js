import { connect } from 'react-redux'

import ActionsBarPortal from './ActionsBarPortal'

export const mapStateToProps = state => {
  return {
    isVisible: state.actionsBar.actionsBarVisibility,
  }
}

export default connect(mapStateToProps)(ActionsBarPortal)
