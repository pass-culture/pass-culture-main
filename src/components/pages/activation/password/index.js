/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import FormInputs from './FormInputs'
import FormWrapper from './FormWrapper'
import { FormFooter } from '../../../forms'
import { mapStateToProps, mapDispatchToProps } from './connect'

export class RawActivationPassword extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { isLoading: false }
  }

  handleActivationLoginRequestFail = () => {
    // redirect to error page
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
    const nextstate = { isLoading: true }
    this.setState(nextstate, () => {
      // TODO Redirect to success
      // resolve form without errors
      formResolver()
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
    return (
      <FormWrapper
        isLoading={isLoading}
        initialValues={initialValues}
        onFormSubmit={this.onFormSubmit}
        className="pc-final-form is-full-layout"
      >
        {(canSubmit, formValues, formErrors) => (
          <div
            id="reset-password-page-request"
            className="is-full-layout flex-rows"
          >
            <main role="main" className="pc-main is-white-text flex-1">
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
          </div>
        )}
      </FormWrapper>
    )
  }
}

RawActivationPassword.propTypes = {
  initialValues: PropTypes.object.isRequired,
  loginUserAfterPasswordSaveSuccess: PropTypes.func.isRequired,
  sendActivationPasswordForm: PropTypes.func.isRequired,
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(RawActivationPassword)
