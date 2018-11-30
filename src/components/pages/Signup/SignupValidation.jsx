import React, { PureComponent } from 'react'
import { Redirect, withRouter } from 'react-router-dom'
import { requestData, showNotification } from 'pass-culture-shared'
import { compose } from 'redux'
import { connect } from 'react-redux'

class SignupValidation extends PureComponent {
  componentDidMount() {
    const {
      dispatch,
      match: {
        params: { token },
      },
    } = this.props

    dispatch(
      requestData('GET', `validate/user/${token}`, {
        handleSuccess: () => {
          dispatch(
            showNotification({
              text:
                'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.',
              type: 'success',
            })
          )
        },
        handleFail: (state, action) => {
          dispatch(
            showNotification({
              text: action.errors.global,
              type: 'danger',
            })
          )
        },
      })
    )
  }

  render() {
    return <Redirect to="/connexion" />
  }
}

export default compose(
  withRouter,
  connect()
)(SignupValidation)
