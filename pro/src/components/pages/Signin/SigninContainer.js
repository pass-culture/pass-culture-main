import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { isAPISireneAvailable } from 'store/features/selectors'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { signin } from 'store/user/thunks'

import Signin from './Signin'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
    isAccountCreationAvailable: isAPISireneAvailable(state),
  }
}

export const mapDispatchToProps = dispatch => ({
  showErrorNotification: errorText =>
    dispatch(
      showNotification({
        type: 'error',
        text: errorText,
      })
    ),
  submit: (emailValue, passwordValue, success, fail) => {
    dispatch(signin(emailValue, passwordValue, success, fail))
  },
})

export default compose(
  withRouter,
  connect(mapStateToProps, mapDispatchToProps)
)(Signin)
