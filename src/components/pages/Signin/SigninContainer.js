import { connect } from 'react-redux'
import { compose } from 'redux'
import { withNotRequiredLogin } from '../../hocs'
import Signin from './Signin'
import { isAPISireneAvailable } from '../../../selectors/data/featuresSelectors'
import { requestData } from 'redux-saga-data'

export const mapStateToProps = state => {
  return {
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

export default compose(
  withNotRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Signin)
