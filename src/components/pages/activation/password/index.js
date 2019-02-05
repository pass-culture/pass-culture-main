/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Form } from 'react-final-form'
import { Redirect } from 'react-router-dom'

import FormInputs from './inputs'
import { canSubmitForm } from '../utils'
import { FormFooter } from '../../../forms'
import { mapStateToProps, mapDispatchToProps } from './connect'

class ActivationPassword extends React.PureComponent {
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
    // resolve form with errors
    this.setState(nextstate, () => {
      const errors =
        (Array.isArray(action.errors) && action.errors[0]) || action.errors
      formResolver(errors)
    })
  }

  loginActivatedUserRequestSuccess = formResolver => () => {
    const { history } = this.props
    const nextstate = { isLoading: true }
    this.setState(nextstate, () => {
      // resolve form without errors
      formResolver()
      history.replace('/decouverte?from=password')
    })
  }

  savePasswordRequestSuccess = (formResolver, formValues) => () => {
    const { loginUserAfterPasswordSaveSuccess } = this.props
    const nextstate = { isLoading: true }
    this.setState(nextstate, () => {
      loginUserAfterPasswordSaveSuccess(
        { ...formValues },
        // simulate form promise resolver
        this.handleActivationLoginRequestFail,
        this.loginActivatedUserRequestSuccess(formResolver)
      )
    })
  }

  onFormSubmit = formValues => {
    this.setState({ isLoading: true })
    const { sendActivationPasswordForm } = this.props
    const promise = sendActivationPasswordForm(
      { ...formValues },
      this.handleActivationPasswordRequestFail,
      this.savePasswordRequestSuccess
    )
    return promise
  }

  render() {
    const { isLoading } = this.state
    const { initialValues } = this.props
    const isValidURL =
      initialValues && initialValues.email && initialValues.token
    if (!isValidURL) {
      return <Redirect to="/activation/error" />
    }
    return (
      <div id="activation-password-page" className="flex-rows">
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

ActivationPassword.propTypes = {
  history: PropTypes.object.isRequired,
  initialValues: PropTypes.object.isRequired,
  loginUserAfterPasswordSaveSuccess: PropTypes.func.isRequired,
  sendActivationPasswordForm: PropTypes.func.isRequired,
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ActivationPassword)
