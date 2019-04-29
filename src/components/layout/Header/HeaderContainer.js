import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Header from './Header'
import mapStateToProps from './mapStateToProps'

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Header)
