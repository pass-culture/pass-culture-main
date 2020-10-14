import { connect } from 'react-redux'

import ActionsBar from './ActionsBar'

export const mapStateToProps = state => {
  return {
    isVisible: state.actionsBar.actionsBarVisibility,
  }
}

export default connect(mapStateToProps)(ActionsBar)
