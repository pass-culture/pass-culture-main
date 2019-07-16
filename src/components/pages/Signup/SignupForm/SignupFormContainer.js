import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { connect } from 'react-redux'
import get from 'lodash.get'
import SignupForm from './SignupForm'

export const mapStateToProps = state => {
  return {
    offererName: get(state, `form.user.name`),
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(SignupForm)
