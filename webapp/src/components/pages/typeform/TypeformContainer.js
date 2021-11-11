import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import Typeform from './Typeform'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import { updateCurrentUser } from '../../../redux/actions/currentUser'
import { selectCurrentUser } from '../../../redux/selectors/currentUserSelector'

function mapStateToProps(state) {
  const user = selectCurrentUser(state)
  return { userId: user.pk }
}

export default compose(
  withRequiredLogin,
  withRouter,
  connect(mapStateToProps, { updateCurrentUser })
)(Typeform)
