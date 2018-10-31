/*
 * Signin
 */

import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import { withLogin } from 'pass-culture-shared'

import component from './component'

export default compose(
  withLogin({ successRedirect: '/decouverte' }),
  withRouter,
  connect()
)(component)
