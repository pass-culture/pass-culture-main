import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Header from './Header'

const mapStateToProps = state => {
  const name = state.user && state.user.publicName

  return {
    name,
    offerers: state.data.offerers,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Header)
