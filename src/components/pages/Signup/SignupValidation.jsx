import React, { PureComponent } from 'react'
import { Redirect, withRouter } from 'react-router-dom'
import { showNotification } from 'pass-culture-shared'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

class SignupValidation extends PureComponent {
  componentDidMount() {
    const {
      dispatch,
      match: {
        params: { token },
      },
    } = this.props

    dispatch(
      requestData({
        apiPath: `/validate/user/${token}`,
        method: 'PATCH',
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
          const {
            payload: { errors },
          } = action
          dispatch(
            showNotification({
              text: errors.global,
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

export default SignupValidation
