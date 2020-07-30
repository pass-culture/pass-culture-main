import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import Typeform from './Typeform'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import { updateCurrentUser } from '../../../redux/actions/currentUser'

export default compose(
  withRequiredLogin,
  withRouter,
  connect(
    null,
    { updateCurrentUser }
  )
)(Typeform)
