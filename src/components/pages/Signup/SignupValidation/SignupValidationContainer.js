import { connect } from 'react-redux'
import withRouter from 'react-router-dom/es/withRouter'
import { compose } from 'redux'

import SignupValidation from './SignupValidation'


export default compose(
  withRouter,
  connect()
)(SignupValidation)
