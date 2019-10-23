import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Form } from 'react-final-form'
import { Link } from 'react-router-dom'

import validateRequiredField from '../../forms/validators/validateRequiredField'
import EmailField from '../../forms/inputs/EmailField'
import PasswordField from '../../forms/inputs/PasswordField'
import canSubmitForm from './canSubmitForm'
import FormFooter from '../../forms/FormFooter'
import parseSubmitErrors from '../../forms/utils/parseSubmitErrors'

const submitButtonOptions = {
  className: 'is-bold is-white-text',
  id: 'signin-submit-button',
  label: 'Connexion',
}

const signUpLinkOption = {
  className: 'is-white-text',
  id: 'sign-up-link',
  label: 'Créer un compte',
  target: '_blank',
  url: 'https://www.demarches-simplifiees.fr/commencer/inscription-pass-culture',
}

class Signin extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { isLoading: false }
  }

  handleRequestFail = formResolver => (state, action) => {
    const nextstate = { isLoading: false }
    const {
      payload: { errors },
    } = action

    const errorsByKey = parseSubmitErrors(errors)
    this.setState(nextstate, () => formResolver(errorsByKey))
  }

  handleRequestSuccess = formResolver => () => {
    const { history, query } = this.props
    const nextstate = { isLoading: false }
    const queryParams = query.parse()
    this.setState(nextstate, () => {
      formResolver()
      const nextUrl = queryParams.from ? decodeURIComponent(queryParams.from) : '/decouverte'
      history.push(nextUrl)
    })
  }

  handleOnFormSubmit = formValues => {
    const { submitSigninForm } = this.props

    this.setState({ isLoading: true })

    return submitSigninForm(formValues, this.handleRequestFail, this.handleRequestSuccess)
  }

  renderForm = formProps => {
    const { isLoading } = this.state
    const canSubmit = !isLoading && canSubmitForm(formProps)
    const { handleSubmit } = formProps

    return (
      <form
        autoComplete="off"
        className="logout-form-container"
        disabled={isLoading}
        noValidate
        onSubmit={handleSubmit}
      >
        <div>
          <div className="logout-form-header">
            <div className="logout-form-header-sup">{'Bonjour !'}</div>
            <div className="logout-form-title">{'Identifiez-vous'}</div>
            <div className="logout-form-title">{'pour accéder aux offres.'}</div>
            <div className="logout-form-mandatory-label">{'* Champs obligatoires'}</div>
          </div>
          <EmailField
            id="user-identifier"
            label="Adresse e-mail"
            name="identifier"
            placeholder="Identifiant (e-mail)"
            required
          />
          <PasswordField
            id="user-password"
            label="Mot de passe"
            name="password"
            placeholder="Mot de passe"
            required={validateRequiredField}
          />
          <Link
            className="logout-form-link"
            to="/mot-de-passe-perdu"
          >
            {'Mot de passe oublié ?'}
          </Link>
        </div>
        <FormFooter
          externalLink={signUpLinkOption}
          submit={{ ...submitButtonOptions, disabled: !canSubmit }}
        />
      </form>
    )
  }

  render() {
    return (
      <main className="logout-form-main">
        <Form
          onSubmit={this.handleOnFormSubmit}
          render={this.renderForm}
        />
      </main>
    )
  }
}

Signin.propTypes = {
  history: PropTypes.shape().isRequired,
  query: PropTypes.shape().isRequired,
  submitSigninForm: PropTypes.func.isRequired,
}

export default Signin
