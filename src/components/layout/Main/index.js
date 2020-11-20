import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Main from './Main'
import mapStateToProps from './mapStateToProps'

export default compose(withRouter, connect(mapStateToProps))(Main)
