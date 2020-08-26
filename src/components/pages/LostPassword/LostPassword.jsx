import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Link } from 'react-router-dom'

import Logo from '../../layout/Logo'
import Main from '../../layout/Main'
import Icon from '../../layout/Icon'

class LostPassword extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      emailValue: '',
      hasPasswordResetRequestErrorMessage: false,
      hasPasswordResetErrorMessage: false,
      newPasswordErrorMessage: '',
      newPasswordValue: '',
    }
  }

  onHandleSuccessRedirectForResetPassword = () => {
    const { history } = this.props
    history.push('/mot-de-passe-perdu?change=1')
  }

  onHandleFailForResetPasswordRequest = () =>
    this.setState({ hasPasswordResetRequestErrorMessage: true })

  onHandleFailForResetPassword = (state, action) => {
    if (action.payload.errors.newPassword) {
      this.setState({ newPasswordErrorMessage: action.payload.errors.newPassword[0] })
    } else {
      this.setState({ hasPasswordResetErrorMessage: true })
    }
  }

  storeValue = token => () => token

  onHandleSuccessRedirectForResetPasswordRequest = () => {
    const { history } = this.props
    history.push('/mot-de-passe-perdu?envoye=1')
  }

  submitResetPasswordRequest = () => {
    const { submitResetPasswordRequest } = this.props
    const { emailValue } = this.state

    return submitResetPasswordRequest(
      emailValue,
      this.onHandleSuccessRedirectForResetPasswordRequest,
      this.onHandleFailForResetPasswordRequest
    )
  }

  submitResetPassword = () => {
    const { submitResetPassword, token } = this.props
    const { newPasswordValue } = this.state

    return submitResetPassword(
      newPasswordValue,
      token,
      this.onHandleSuccessRedirectForResetPassword,
      this.onHandleFailForResetPassword
    )
  }

  handleInputEmailChange = event => {
    this.setState({ emailValue: event.target.value })
    this.setState({ hasPasswordResetRequestErrorMessage: false })
  }

  handleInputPasswordChange = event => {
    this.setState({ newPasswordValue: event.target.value })
    this.setState({ hasPasswordResetErrorMessage: false })
  }

  render() {
    const {
      hasPasswordResetRequestErrorMessage,
      hasPasswordResetErrorMessage,
      newPasswordErrorMessage,
      emailValue,
      newPasswordValue,
    } = this.state
    const { change, envoye, token } = this.props

    return (
      <Main
        fullscreen
        name="sign-in"
      >
        <div className="logo-side">
          <Logo
            noLink
            signPage
          />
        </div>
        <div className="container">
          <div className="columns">
            <div className="column is-offset-6 is-two-fifths sign-page-form">
              {change && (
                <section className="hero has-text-grey">
                  <div className="hero-body">
                    <h1 className="title is-spaced is-1">
                      <span className="has-text-weight-normal">
                        {'Mot de passe changé !'}
                      </span>
                    </h1>
                    <h2 className="subtitle is-2">
                      {'Vous pouvez dès à présent vous connecter avec votre nouveau mot de passe'}
                    </h2>

                    <Link
                      className="primary-link"
                      to="/connexion"
                    >
                      {'Se connecter'}
                    </Link>
                  </div>
                </section>
              )}
              {envoye && (
                <section className="hero has-text-grey">
                  <div className="hero-body">
                    <h1 className="title is-spaced is-1">
                      <span className="has-text-weight-normal">
                        {'Merci !'}
                      </span>
                    </h1>
                    <h2 className="subtitle is-2">
                      {
                        'Vous allez recevoir par e-mail les instructions pour définir un nouveau mot de passe.'
                      }
                    </h2>

                    <Link
                      className="primary-link"
                      to="/accueil"
                    >
                      {'Revenir à l’accueil'}
                    </Link>
                  </div>
                </section>
              )}
              {token && (
                <section className="hero has-text-grey">
                  <div className="hero-body">
                    <h1 className="title is-spaced is-1">
                      <span className="has-text-weight-normal">
                        {'Créer un nouveau mot de passe'}
                      </span>
                    </h1>
                    <h2 className="subtitle is-2">
                      {'Saisissez le nouveau mot de passe'}
                    </h2>
                    <span className="has-text-grey">
                      <span className="required-legend">
                        {'*'}
                      </span>
                      {' Champs obligatoires'}
                    </span>
                    {hasPasswordResetErrorMessage && (
                      <div className="server-error-message">
                        <Icon svg="picto-warning" />
                        <span>
                          {"Une erreur s'est produite, veuillez réessayer ultérieurement."}
                        </span>
                      </div>
                    )}
                    <form>
                      <label className="input-text">
                        {'Nouveau mot de passe'}
                        <span className="field-asterisk">
                          {'*'}
                        </span>
                        <input
                          className="it-input"
                          onChange={this.handleInputPasswordChange}
                          placeholder="*****"
                          required
                          type="password"
                          value={newPasswordValue}
                        />
                        {newPasswordErrorMessage && (
                          <div className="password-error-message">
                            <Icon svg="picto-warning" />
                            <pre>
                              {newPasswordErrorMessage}
                            </pre>
                          </div>
                        )}
                      </label>
                      <button
                        className="primary-button"
                        onClick={this.submitResetPassword}
                        type="button"
                      >
                        {'Envoyer'}
                      </button>
                    </form>
                  </div>
                </section>
              )}
              {!token && !envoye && !change && (
                <section className="hero has-text-grey">
                  <div className="hero-body">
                    <h1 className="title is-spaced is-1">
                      <span className="has-text-weight-normal">
                        {'Mot de passe égaré ?'}
                      </span>
                    </h1>
                    <h2 className="subtitle is-2">
                      {
                        'Indiquez ci-dessous l’adresse e-mail avec laquelle vous avez créé votre compte.'
                      }
                    </h2>
                    <span className="has-text-grey">
                      <span className="required-legend">
                        {'*'}
                      </span>
                      {'Champs obligatoires'}
                    </span>
                    {hasPasswordResetRequestErrorMessage && (
                      <div className="server-error-message">
                        <Icon svg="picto-warning" />
                        <span>
                          {"Une erreur s'est produite, veuillez réessayer ultérieurement."}
                        </span>
                      </div>
                    )}
                    <form>
                      <label className="input-text">
                        {'Adresse e-mail'}
                        <span className="field-asterisk">
                          {'*'}
                        </span>
                        <input
                          className="it-input"
                          onChange={this.handleInputEmailChange}
                          placeholder="Identifiant (e-mail)"
                          required
                          type="email"
                          value={emailValue}
                        />
                      </label>
                      <button
                        className="primary-button"
                        onClick={this.submitResetPasswordRequest}
                        type="button"
                      >
                        {'Envoyer'}
                      </button>
                    </form>
                  </div>
                </section>
              )}
            </div>
          </div>
        </div>
      </Main>
    )
  }
}

LostPassword.propTypes = {
  change: PropTypes.bool.isRequired,
  envoye: PropTypes.bool.isRequired,
  submitResetPassword: PropTypes.func.isRequired,
  submitResetPasswordRequest: PropTypes.func.isRequired,
  token: PropTypes.string.isRequired,
}

export default LostPassword
