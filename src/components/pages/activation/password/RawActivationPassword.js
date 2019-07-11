import React from 'react'
import PropTypes from 'prop-types'
import { Redirect } from 'react-router'
import { Form } from 'react-final-form'
import canSubmitForm from './canSubmitForm'
import FormInputs from './FormInputs'
import { FormFooter } from '../../../forms'

class RawActivationPassword extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { isLoading: false }
  }

  componentDidMount() {
    const { checkTokenIsValid, initialValues, hasTokenBeenChecked } = this.props

    if (!hasTokenBeenChecked) {
      checkTokenIsValid(initialValues.token)
    }
  }

  handleActivationLoginRequestFail = () => {
    const { history } = this.props
    history.push('/activation/error')
  }

  handleActivationPasswordRequestFail = formResolver => (state, action) => {
    const nextstate = { isLoading: false }
    const {
      payload: { errors },
    } = action
    // resolve form with errors
    this.setState(nextstate, () => {
      const error = (Array.isArray(errors) && errors[0]) || errors
      formResolver(error)
    })
  }

  loginActivatedUserRequestSuccess = formResolver => () => {
    const { history } = this.props
    formResolver()
    history.replace('/typeform?from=password')
  }

  savePasswordRequestSuccess = (formResolver, formValues) => () => {
    const { loginUserAfterPasswordSaveSuccess } = this.props
    loginUserAfterPasswordSaveSuccess(
      { ...formValues },
      this.handleActivationLoginRequestFail,
      this.loginActivatedUserRequestSuccess(formResolver)
    )
  }

  handleOnFormSubmit = formValues => {
    this.setState({ isLoading: true })
    const { sendActivationPasswordForm } = this.props
    const promise = sendActivationPasswordForm(
      { ...formValues },
      this.handleActivationPasswordRequestFail,
      this.savePasswordRequestSuccess
    )
    return promise
  }

  renderForm = formProps => {
    const { isLoading } = this.state
    const formValues = formProps.values || {}
    const canSubmit = !isLoading && canSubmitForm(formProps)
    const formErrors = !formProps.pristine && formProps.error
    return (
      <form
        autoComplete="off"
        className="pc-final-form is-full-layout flex-rows"
        disabled={isLoading}
        noValidate
        onSubmit={formProps.handleSubmit}
      >
        <main
          className="pc-main padded-2x is-white-text"
          role="main"
        >
          <FormInputs
            formErrors={formErrors}
            formValues={formValues}
            isLoading={isLoading}
          />
        </main>
        <FormFooter
          submit={{
            className: 'is-bold is-white-text',
            disabled: !canSubmit,
            label: 'Enregistrer',
          }}
        />
      </form>
    )
  }

  render() {
    const { initialValues, isValidUrl, isValidToken, hasTokenBeenChecked } = this.props

    if (!isValidUrl) {
      return <Redirect to="/activation/error" />
    }

    if (hasTokenBeenChecked && !isValidToken) {
      return <Redirect to="/activation/lien-invalide" />
    }

    return (
      <div
        className="pc-scroll-container flex-rows"
        id="activation-password-page"
      >
        <Form
          initialValues={initialValues}
          onSubmit={this.handleOnFormSubmit}
          render={this.renderForm}
        />
      </div>
    )
  }
}

RawActivationPassword.propTypes = {
  checkTokenIsValid: PropTypes.func.isRequired,
  hasTokenBeenChecked: PropTypes.bool.isRequired,
  history: PropTypes.shape().isRequired,
  initialValues: PropTypes.shape().isRequired,
  isValidToken: PropTypes.bool.isRequired,
  isValidUrl: PropTypes.bool.isRequired,
  loginUserAfterPasswordSaveSuccess: PropTypes.func.isRequired,
  sendActivationPasswordForm: PropTypes.func.isRequired,
}

export default RawActivationPassword
