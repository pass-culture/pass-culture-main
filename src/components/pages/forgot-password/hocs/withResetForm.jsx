import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form as FinalForm } from 'react-final-form'
import { connect } from 'react-redux'

import { requestData } from '../../../../utils/fetch-normalize-data/requestData'
import { getReCaptchaToken } from '../../../../utils/recaptcha'
import { IS_DEV } from '../../../../utils/config'

const doNothingFunction = () => {}

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
      this.setState(nextstate, () => formResolver(action.payload.errors))
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
          if (!IS_DEV) {
            getReCaptchaToken('resetPassword').then(token => {
              this.promiseOnFormSubmit({ ...formValues, token: token }, resolve)
            })
          } else {
            this.promiseOnFormSubmit({ ...formValues, token: 'testing_token' }, resolve)
          }
        } else {
          this.promiseOnFormSubmit(formValues, resolve)
        }
      })
      return formSubmitPromise
    }

    // https://github.com/final-form/final-form#formstate
    renderFinalForm = formState => {
      const { isloading } = this.state
      const canSubmit =
        (!formState.pristine &&
          !formState.hasSubmitErrors &&
          !formState.hasValidationErrors &&
          !isloading) ||
        (!formState.hasValidationErrors &&
          formState.hasSubmitErrors &&
          formState.dirtySinceLastSubmit)
      return (
        <form
          autoComplete="off"
          className="logout-form-container"
          disabled={isloading}
          noValidate
          onSubmit={formState.handleSubmit}
        >
          <WrappedComponent
            {...this.props}
            canSubmit={canSubmit}
            hasSubmitErrors={!formState.pristine && formState.hasSubmitErrors}
            hasValidationErrors={!formState.pristine && formState.hasValidationErrors}
            isLoading={isloading}
            validationErrors={formState.errors}
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
          validate={validator || doNothingFunction}
        />
      )
    }
  }

  ResetPasswordForm.defaultProps = {
    initialValues: {},
  }

  ResetPasswordForm.propTypes = resetPasswordFormPropTypes

  return connect()(ResetPasswordForm)
}

const resetPasswordFormPropTypes = {
  dispatch: PropTypes.func.isRequired,
  // NOTE: history et location sont automatiquement
  // injectées par le render de la route du react-router-dom
  history: PropTypes.shape().isRequired,
  initialValues: PropTypes.shape(),
  location: PropTypes.shape().isRequired,
}

export const resetFormWrappedComponentPropTypes = {
  canSubmit: PropTypes.bool.isRequired,
  hasSubmitErrors: PropTypes.bool.isRequired,
  hasValidationErrors: PropTypes.bool.isRequired,
  isLoading: PropTypes.bool.isRequired,
  validationErrors: PropTypes.shape(),
  ...resetPasswordFormPropTypes,
}

export default withResetForm
