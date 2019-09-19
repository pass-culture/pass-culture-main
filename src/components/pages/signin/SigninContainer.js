import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import Signin from './Signin'
import { withNotRequiredLogin } from '../../hocs'

export const mapDispatchToProps = dispatch => ({
  submitSigninForm: (values, fail, success) => {
    const routeMethod = 'POST'
    const routePath = '/users/signin'
    // NOTE: on retourne une promise au formulaire
    // pour pouvoir gérer les erreurs de l'API
    // directement dans les champs du formulaire
    const formSubmitPromise = new Promise(resolve => {
      dispatch(
        requestData({
          apiPath: routePath,
          body: { ...values },
          handleFail: fail(resolve),
          handleSuccess: success(resolve),
          method: routeMethod,
        })
      )
    })
    return formSubmitPromise
  },
})

const SigninContainer = compose(
  withNotRequiredLogin,
  connect(
    null,
    mapDispatchToProps
  )
)(Signin)

export default SigninContainer
