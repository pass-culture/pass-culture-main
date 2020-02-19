import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import { requestData } from 'redux-thunk-data'

import CheckBoxField from '../../forms/inputs/CheckBoxField'
import EmailField from '../../forms/inputs/EmailField'
import InputField from '../../forms/inputs/InputField'
import PasswordField from '../../forms/inputs/PasswordField'
import FormFooter from './FormFooter/FormFooter'
import { getCanSubmit, parseSubmitErrors } from '../../../utils/react-form-utils/functions'

class SignUp extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { isFormLoading: false }
  }

  handleRequestFail = formResolver => (state, action) => {
    // we return API errors back to the form
    const { payload } = action
    const nextState = { isFormLoading: false }
    const errors = parseSubmitErrors(payload.errors)
    this.setState(nextState, () => formResolver(errors))
  }

  handleRequestSuccess = formResolver => () => {
    const { history } = this.props
    const nextState = { isFormLoading: false }
    this.setState(nextState, () => {
      formResolver()
      const nextUrl = '/decouverte'
      history.push(nextUrl)
    })
  }

  handleOnFormSubmit = formValues => {
    const { dispatch } = this.props

    const apiPath = '/users/signup/webapp'
    const method = 'POST'

    this.setState({ isFormLoading: true })
    // NOTE: we need to promise the request callbacks
    // in order to inject their payloads into the form
    const formSubmitPromise = new Promise(resolve => {
      dispatch(
        requestData({
          apiPath,
          body: { ...formValues },
          handleFail: this.handleRequestFail(resolve),
          handleSuccess: this.handleRequestSuccess(resolve),
          method,
          resolve: userFromRequest => Object.assign({ isCurrent: true }, userFromRequest),
        })
      )
    })

    return formSubmitPromise
  }

  successRedirect = () => '/decouverte'

  renderForm = formProps => {
    const { isFormLoading } = this.state
    const { handleSubmit } = formProps

    return (
      <form
        autoComplete="off"
        className="logout-form-container"
        disabled={isFormLoading}
        noValidate
        onSubmit={handleSubmit}
      >
        <div>
          <div className="logout-form-header">
            <div className="logout-form-title">
              {'Une minute pour créer un compte, et puis c’est tout !'}
            </div>
            <div className="logout-form-mandatory-label">
              <span className="asterisk">
                {'*'}
              </span>
              &nbsp;
              {'Champs obligatoires'}
            </div>
          </div>
          <InputField
            autoComplete="name"
            label="Identifiant"
            name="publicName"
            placeholder="Mon nom ou pseudo"
            required
            sublabel="...que verront les autres utilisateurs : "
          />
          <EmailField
            autoComplete="email"
            label="Adresse e-mail"
            name="email"
            placeholder="nom@exemple.fr"
            required
            sublabel="...pour se connecter et récupérer son mot de passe en cas d’oubli : "
          />
          <PasswordField
            autoComplete="new-password"
            label="Mot de passe"
            name="password"
            placeholder="Mon mot de passe"
            required
            sublabel="...pour se connecter : "
          />
          <CheckBoxField name="contact_ok">
            <span>
              {'J’accepte d’être contacté par e-mail pour donner mon avis sur le '}
              <a
                href="http://passculture.beta.gouv.fr"
                rel="noopener noreferrer"
                target="_blank"
              >
                {'pass Culture'}
              </a>
              <span className="asterisk">
                {'*'}
              </span>
            </span>
          </CheckBoxField>
        </div>
        <FormFooter
          isLoading={isFormLoading}
          isSubmit={getCanSubmit(formProps)}
        />
      </form>
    )
  }

  render() {
    return (
      <main className="logout-form-main">
        <Form
          handleSuccessRedirect={this.successRedirect}
          onSubmit={this.handleOnFormSubmit}
          render={this.renderForm}
        />
      </main>
    )
  }
}

SignUp.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
}

export default SignUp
