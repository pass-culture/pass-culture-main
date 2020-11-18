import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form as FinalForm } from 'react-final-form'
import { connect } from 'react-redux'

import { requestData } from '../../../../utils/fetch-normalize-data/requestData'
import { getReCaptchaToken } from '../../../../utils/recaptcha'

const noop = () => {}

const withResetForm = (WrappedComponent, validator, routePath, routeMethod) => {
  const name = WrappedComponent.displayName || 'Component'
  withResetForm.displayName = `withResetForm(${name})`

  class ResetPasswordForm extends PureComponent {
    constructor(props) {
      super(props)
      const { initialValues } = this.props
      this.state = { isloading: false }
      this.initialValues = { ...initialValues }
    }

    handleRequestFail = formResolver => (state, action) => {
      // on retourne les erreurs API au formulaire
      const nextstate = { isloading: false }
      const {
        payload: { errors },
      } = action
      this.setState(nextstate, () => formResolver(errors))
    }

    handleRequestSuccess = formResolver => () => {
      const { history, location } = this.props
      const nextstate = { isloading: false }
      this.setState(nextstate, () => {
        formResolver()
        const baseurl = location.pathname
        const nexturl = `${baseurl}/succes${location.search}`
        history.replace(nexturl)
      })
    }

    promiseOnFormSubmit = (body, resolve) => {
      const { dispatch } = this.props

      const config = {
        apiPath: routePath,
        body,
        handleFail: this.handleRequestFail(resolve),
        handleSuccess: this.handleRequestSuccess(resolve),
        method: routeMethod,
      }
      dispatch(requestData(config))
    }

    handleOnFormSubmit = formValues => {
      this.setState({ isloading: true })

      // NOTE: on retourne une promise au formulaire
      // pour pouvoir gérer les erreurs de l'API
      // directement dans les champs du formulaire
      const formSubmitPromise = new Promise(resolve => {
        if (routePath === '/users/reset-password') {
          getReCaptchaToken('resetPassword').then(token => {
            this.promiseOnFormSubmit({ ...formValues, token: token }, resolve)
          })
        } else {
          this.promiseOnFormSubmit(formValues, resolve)
        }
      })
      return formSubmitPromise
    }

    renderFinalForm = ({
      // https://github.com/final-form/final-form#formstate
      dirtySinceLastSubmit,
      error: preSubmitError,
      handleSubmit,
      hasSubmitErrors,
      hasValidationErrors,
      pristine,
      values,
    }) => {
      const { isloading } = this.state
      const canSubmit =
        (values.newPasswordConfirm === values.newPassword &&
          !pristine &&
          !hasSubmitErrors &&
          !hasValidationErrors &&
          !isloading) ||
        (!hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit)

      return (
        <form
          autoComplete="off"
          className="logout-form-container"
          disabled={isloading}
          noValidate
          onSubmit={handleSubmit}
        >
          <WrappedComponent
            {...this.props}
            canSubmit={canSubmit}
            formErrors={!pristine && preSubmitError}
            isLoading={isloading}
          />
        </form>
      )
    }

    render() {
      return (
        <FinalForm
          initialValues={this.initialValues || {}}
          onSubmit={this.handleOnFormSubmit}
          render={this.renderFinalForm}
          validate={validator || noop}
        />
      )
    }
  }

  ResetPasswordForm.defaultProps = {
    initialValues: {},
  }

  ResetPasswordForm.propTypes = {
    dispatch: PropTypes.func.isRequired,
    // NOTE: history et location sont automatiquement
    // injectées par le render de la route du react-router-dom
    history: PropTypes.shape().isRequired,
    initialValues: PropTypes.shape(),
    location: PropTypes.shape().isRequired,
  }

  return connect()(ResetPasswordForm)
}

export default withResetForm
