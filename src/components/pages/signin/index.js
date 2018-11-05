/*
 * Signin
 */

import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import { withLogin } from 'pass-culture-shared'

import SigninContent from './SigninContent'

export const Signin = compose(
  withLogin({ successRedirect: '/decouverte' }),
  withRouter,
  connect()
)(SigninContent)

export default Signin
