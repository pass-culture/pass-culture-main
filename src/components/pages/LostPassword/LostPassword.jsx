import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Link } from 'react-router-dom'

import Logo from '../../layout/Logo'
import Main from '../../layout/Main'
import TextInput from '../../layout/inputs/TextInput/TextInput'
import TextInputWithIcon from '../../layout/inputs/TextInputWithIcon/TextInputWithIcon'
import GenericError from '../../layout/errors/GenericError'

class LostPassword extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      emailValue: '',
      hasPasswordResetRequestErrorMessage: false,
      hasPasswordResetErrorMessage: false,
      newPasswordErrorMessage: '',
      newPasswordValue: '',
      isPasswordHidden: true,
    }
  }

  redirectToResetPasswordSuccessPage = () => {
    const { history } = this.props
    history.push('/mot-de-passe-perdu?change=1')
  }

  displayPasswordResetErrorMessages = (state, action) => {
    if (action.payload.errors.newPassword) {
      this.setState({ newPasswordErrorMessage: action.payload.errors.newPassword[0] })
    } else {
      this.setState({ hasPasswordResetErrorMessage: true })
    }
  }

  redirectToResetPasswordRequestSuccessPage = () => {
    const { history } = this.props
    history.push('/mot-de-passe-perdu?envoye=1')
  }

  displayPasswordResetRequestErrorMessage = () =>
    this.setState({ hasPasswordResetRequestErrorMessage: true })

  submitResetPasswordRequest = event => {
    event.preventDefault()
    const { submitResetPasswordRequest } = this.props
    const { emailValue } = this.state

    return submitResetPasswordRequest(
      emailValue,
      this.redirectToResetPasswordRequestSuccessPage,
      this.displayPasswordResetRequestErrorMessage
    )
  }

  submitResetPassword = event => {
    event.preventDefault()
    const { submitResetPassword, token } = this.props
    const { newPasswordValue } = this.state

    return submitResetPassword(
      newPasswordValue,
      token,
      this.redirectToResetPasswordSuccessPage,
      this.displayPasswordResetErrorMessages
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

  handleToggleHidden = event => {
    event.preventDefault()
    this.setState(previousState => ({
      isPasswordHidden: !previousState.isPasswordHidden,
    }))
  }

  isResetPasswordRequestSubmitDisabled = () => {
    const { emailValue } = this.state

    return emailValue === ''
  }

  isResetPasswordSubmitDisabled = () => {
    const { newPasswordValue } = this.state

    return newPasswordValue === ''
  }

  render() {
    const {
      emailValue,
      hasPasswordResetRequestErrorMessage,
      hasPasswordResetErrorMessage,
      newPasswordErrorMessage,
      isPasswordHidden,
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
                <section className="hero password-reset">
                  <div className="hero-body">
                    <h1>
                      {'Mot de passe changé !'}
                    </h1>
                    <h2>
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
                <section className="hero mail-sent">
                  <div className="hero-body">
                    <h1>
                      {'Merci !'}
                    </h1>
                    <h2>
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
                <section className="hero password-reset-request-form">
                  <div className="hero-body">
                    <h1>
                      {'Créer un nouveau mot de passe'}
                    </h1>
                    <h2>
                      {'Saisissez le nouveau mot de passe'}
                    </h2>

                    {hasPasswordResetErrorMessage && (
                      <GenericError
                        message={"Une erreur s'est produite, veuillez réessayer ultérieurement."}
                      />
                    )}
                    <form
                      className="new-password-form"
                      onSubmit={this.submitResetPassword}
                    >
                      <TextInputWithIcon
                        error={newPasswordErrorMessage ? newPasswordErrorMessage : null}
                        icon={isPasswordHidden ? 'ico-eye-close' : 'ico-eye-open'}
                        iconAlt={
                          isPasswordHidden ? 'Afficher le mot de passe' : 'Cacher le mot de passe'
                        }
                        label="Nouveau mot de passe"
                        name="password"
                        onChange={this.handleInputPasswordChange}
                        onIconClick={this.handleToggleHidden}
                        placeholder="Mon nouveau mot de passe"
                        required
                        sublabel="obligatoire"
                        type={isPasswordHidden ? 'password' : 'text'}
                        value={newPasswordValue}
                      />

                      <button
                        className="primary-button submit-button"
                        disabled={this.isResetPasswordSubmitDisabled()}
                        type="submit"
                      >
                        {'Envoyer'}
                      </button>
                    </form>
                  </div>
                </section>
              )}
              {!token && !envoye && !change && (
                <section className="hero password-reset-request">
                  <div className="hero-body">
                    <h1>
                      {'Mot de passe égaré ?'}
                    </h1>
                    <h2>
                      {
                        'Indiquez ci-dessous l’adresse e-mail avec laquelle vous avez créé votre compte.'
                      }
                    </h2>

                    {hasPasswordResetRequestErrorMessage && (
                      <GenericError
                        message={"Une erreur s'est produite, veuillez réessayer ultérieurement."}
                      />
                    )}

                    <form onSubmit={this.submitResetPasswordRequest}>
                      <TextInput
                        label="Adresse e-mail"
                        name="email"
                        onChange={this.handleInputEmailChange}
                        placeholder="nom@exemple.fr"
                        required
                        sublabel="obligatoire"
                        type="email"
                        value={emailValue}
                      />

                      <button
                        className="primary-button"
                        disabled={this.isResetPasswordRequestSubmitDisabled()}
                        type="submit"
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
