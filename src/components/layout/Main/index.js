import { withBlock } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Main from './Main'
import mapStateToProps from './mapStateToProps'

export default compose(
  withRouter,
  withBlock,
  connect(mapStateToProps)
)(Main)
