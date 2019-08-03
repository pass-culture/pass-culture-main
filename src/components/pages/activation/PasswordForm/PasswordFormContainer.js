import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import PasswordForm from './PasswordForm'
import withFrenchQueryRouter from '../../../hocs/withFrenchQueryRouter'
import { setTokenStatus, validateToken } from '../../../../reducers/token'

import doesTokenHaveBeenChecked from './helpers/doesTokenHaveBeenChecked'
import isValidToken from './helpers/isValidToken'

export const mapDispatchToProps = dispatch => ({
  checkTokenIsValid: token =>
    validateToken(token, dispatch).then(tokenStatus => {
      dispatch(setTokenStatus(tokenStatus))
    }),

  loginUserAfterPasswordSaveSuccess: (values, fail, success) => {
    const { email: identifier, newPassword: password } = values
    const config = {
      apiPath: '/users/signin',
      body: { identifier, password },
      handleFail: fail,
      handleSuccess: success,
      method: 'POST',
    }
    dispatch(requestData(config))
  },

  sendPassword: (values, fail, success) =>
    // NOTE: on retourne une promise au formulaire
    // pour pouvoir gérer les erreurs de l'API
    // directement dans les champs du formulaire
    new Promise(resolve => {
      const config = {
        apiPath: '/users/new-password',
        body: { ...values },
        handleFail: fail(resolve),
        handleSuccess: success(resolve, values),
        method: 'POST',
        stateKey: 'activatedUserCredentials',
      }
      dispatch(requestData(config))
    }),
})

export const mapStateToProps = (state, ownProps) => {
  const { match, query } = ownProps
  const { params } = match
  const { token } = params
  const queryParams = query.parse()
  const { email } = queryParams
  const initialValues = { email, token }
  const isValidUrl = Boolean(token && email)

  return {
    hasTokenBeenChecked: doesTokenHaveBeenChecked(state),
    initialValues,
    isValidToken: isValidToken(state),
    isValidUrl,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(PasswordForm)
