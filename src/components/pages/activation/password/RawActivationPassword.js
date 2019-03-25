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
    history.replace('/decouverte?from=password')
  }

  savePasswordRequestSuccess = (formResolver, formValues) => () => {
    const { loginUserAfterPasswordSaveSuccess } = this.props
    loginUserAfterPasswordSaveSuccess(
      { ...formValues },
      this.handleActivationLoginRequestFail,
      this.loginActivatedUserRequestSuccess(formResolver)
    )
  }

  onFormSubmit = formValues => {
    this.setState({ isLoading: true })
    const { sendActivationPasswordForm } = this.props
    return sendActivationPasswordForm(
      { ...formValues },
      this.handleActivationPasswordRequestFail,
      this.savePasswordRequestSuccess
    )
  }

  render() {
    const { isLoading } = this.state
    const { initialValues, isValidUrl } = this.props

    if (!isValidUrl) {
      return <Redirect to="/activation/error" />
    }
    return (
      <div
        id="activation-password-page"
        className="pc-scroll-container flex-rows"
      >
        <Form
          onSubmit={this.onFormSubmit}
          initialValues={initialValues}
          render={formProps => {
            const formValues = formProps.values || {}
            const canSubmit = !isLoading && canSubmitForm(formProps)
            const formErrors = !formProps.pristine && formProps.error
            return (
              <form
                noValidate
                autoComplete="off"
                disabled={isLoading}
                onSubmit={formProps.handleSubmit}
                className="pc-final-form is-full-layout flex-rows"
              >
                <main role="main" className="pc-main padded-2x is-white-text">
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
          }}
        />
      </div>
    )
  }
}

RawActivationPassword.propTypes = {
  history: PropTypes.object.isRequired,
  initialValues: PropTypes.object.isRequired,
  isValidUrl: PropTypes.bool.isRequired,
  loginUserAfterPasswordSaveSuccess: PropTypes.func.isRequired,
  sendActivationPasswordForm: PropTypes.func.isRequired,
}

export default RawActivationPassword
