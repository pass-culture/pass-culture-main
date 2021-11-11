import { parse } from 'query-string'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { setTokenStatus, validateToken } from '../../../../redux/actions/token'
import { requestData } from '../../../../utils/fetch-normalize-data/requestData'
import doesTokenHaveBeenChecked from './helpers/doesTokenHaveBeenChecked'
import isValidToken from './helpers/isValidToken'
import PasswordForm from './PasswordForm'

export const mapDispatchToProps = dispatch => ({
  checkTokenIsValid: token =>
    validateToken(token, dispatch).then(tokenStatus => {
      dispatch(setTokenStatus(tokenStatus))
    }),

  loginUserAfterPasswordSaveSuccess: (values, fail, success) => {
    const { email: identifier, newPassword: password } = values
    const config = {
      apiPath: '/beneficiaries/signin',
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
  const { location, match } = ownProps
  const { params } = match
  const { token } = params
  const { email } = parse(location.search)
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
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(PasswordForm)
