/*
* @debt deprecated "Gaël: deprecated usage of redux-saga-data"
* @debt standard "Gaël: prefer hooks for routers (https://reactrouter.com/web/api/Hooks)"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { isAPISireneAvailable } from 'store/features/selectors'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

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
    dispatch(
      requestData({
        apiPath: '/users/signin',
        body: { identifier: emailValue, password: passwordValue },
        handleFail: fail,
        handleSuccess: success,
        method: 'POST',
      })
    )
  },
})

export default compose(withRouter, connect(mapStateToProps, mapDispatchToProps))(Signin)
