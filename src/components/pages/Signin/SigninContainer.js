import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { isAPISireneAvailable } from 'store/selectors/data/featuresSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import Signin from './Signin'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
    isAccountCreationAvailable: isAPISireneAvailable(state),
  }
}

export const mapDispatchToProps = dispatch => ({
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
