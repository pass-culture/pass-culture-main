import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Form } from 'react-final-form'
import { Link } from 'react-router-dom'
import EmailField from '../../forms/inputs/EmailField'
import PasswordField from '../../forms/inputs/PasswordField'
import canSubmitForm from './utils/canSubmitForm'
import FormFooter from '../../forms/FormFooter'
import parseSubmitErrors from '../../forms/utils/parseSubmitErrors'

class SignIn extends PureComponent {
  constructor(props) {
    super(props)
  }

  handleFail = formResolver => (state, action) => {
    const {
      payload: { errors },
    } = action

    const formErrors = parseSubmitErrors(errors)
    formResolver(formErrors)
  }

  handleSuccess = (formResolver) => () => {
    const { history } = this.props
    formResolver()
    history.push('/decouverte')
  }

  handleSubmit = formValues => {
    const { signIn } = this.props

    return signIn(
      formValues,
      this.handleFail,
      this.handleSuccess
    )
  }

  renderForm = props => {
    const canSubmit = canSubmitForm(props)
    const { handleSubmit } = props

    return (
      <form
        autoComplete="off"
        className="lf-container"
        noValidate
        onSubmit={handleSubmit}
      >
        <div>
          <div className="lf-header">
            <h1 className="lf-title">
              {'Connexion'}
            </h1>
            <h2 className="lf-subtitle">
              {'Identifiez-vous\n'}
              {'pour accéder aux offres'}
            </h2>
          </div>
          <EmailField
            id="user-identifier"
            label="Adresse e-mail"
            name="identifier"
            placeholder="Ex : nom@domaine.fr"
          />
          <PasswordField
            id="user-password"
            label="Mot de passe"
            name="password"
            placeholder="Ex : IoPms44*"
          />
          <Link
            className="lf-lost-password"
            to="/mot-de-passe-perdu"
          >
            {'Mot de passe oublié ?'}
          </Link>
        </div>
        <FormFooter
          cancel={{
            disabled: false,
            id: 'cancel-link',
            label: 'Annuler',
            url: '/beta',
          }}
          submit={{
            disabled: !canSubmit,
            id: 'sign-in-button',
            label: 'Connexion',
          }}
        />
      </form>
    )
  }

  render() {
    return (
      <main className="login-form-main">
        <Form
          onSubmit={this.handleSubmit}
          render={this.renderForm}
        />
      </main>
    )
  }
}

SignIn.propTypes = {
  history: PropTypes.shape().isRequired,
  signIn: PropTypes.func.isRequired,
}

export default SignIn
