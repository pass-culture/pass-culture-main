import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Form } from 'react-final-form'
import { Link } from 'react-router-dom'
import EmailField from '../../forms/inputs/EmailField'
import PasswordField from '../../forms/inputs/PasswordField'
import canSubmitForm from './utils/canSubmitForm'
import FormError from '../../forms/FormError'
import FormFooter from '../../forms/FormFooter'
import parseSubmitErrors from '../../forms/utils/parseSubmitErrors'
import { campaignTracker } from '../../../tracking/mediaCampaignsTracking'
import validateEmailField from '../../forms/validators/validateEmailField'
import validatePasswordField from '../../forms/validators/validatePasswordField'

class SignIn extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      genericError: '',
    }
  }

  componentDidMount() {
    campaignTracker.signin()
  }

  handleFail = formResolver => (state, action) => {
    const {
      payload: { errors, status },
    } = action

    const formErrors = parseSubmitErrors(errors)

    if (formErrors.signin) {
      this.setState({ genericError: formErrors.signin[0] })
    } else if (status === 429) {
      this.setState({
        genericError: 'Nombre de tentatives de connexion dépassé. Réessaye dans 1 minute.',
      })
    }

    formResolver(formErrors)
  }

  handleSuccess = formResolver => () => {
    const { history, homepageIsDisabled } = this.props
    formResolver()
    const nextPath = homepageIsDisabled ? '/decouverte' : '/accueil'
    history.push(nextPath)
  }

  handleSubmit = formValues => {
    const { signIn } = this.props

    return signIn(formValues, this.handleFail, this.handleSuccess)
  }

  renderForm = props => {
    const canSubmit = canSubmitForm(props)
    const { handleSubmit } = props
    const { genericError } = this.state
    const displayErrorMessage = !props.dirtySinceLastSubmit

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
              {'Identifie-toi\n'}
              {'pour accéder aux offres'}
            </h2>
          </div>
          <span className="mandatory-fields">
            {'* Champs obligatoires'}
          </span>
          <EmailField
            id="user-identifier"
            label="Adresse e-mail"
            name="identifier"
            placeholder="Exemple : nom@domaine.fr"
            required={validateEmailField}
          />
          <PasswordField
            id="user-password"
            label="Mot de passe"
            name="password"
            placeholder="Exemple : IoPms44*"
            required={validatePasswordField}
          />
          {displayErrorMessage && <FormError customMessage={genericError} />}

          <Link
            className="lf-lost-password"
            to="/mot-de-passe-perdu"
          >
            {'Mot de passe oublié ?'}
          </Link>
        </div>
        <FormFooter
          items={[
            {
              disabled: false,
              id: 'cancel-link',
              label: 'Annuler',
              url: '/beta',
            },
            {
              disabled: !canSubmit,
              id: 'sign-in-button',
              label: 'Connexion',
            },
          ]}
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

SignIn.defaultProps = {
  homepageIsDisabled: true,
}

SignIn.propTypes = {
  history: PropTypes.shape().isRequired,
  homepageIsDisabled: PropTypes.bool,
  signIn: PropTypes.func.isRequired,
}

export default SignIn
