import { Field, Form, SubmitButton } from 'pass-culture-shared'
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
      hasErrorMessage: false,
    }
  }
  onHandleSuccessRedirectForResetPassword = () => '/mot-de-passe-perdu?change=1'

  onHandleFail = () => this.setState({ hasErrorMessage: true })

  storeValue = token => () => token

  onHandleSuccessRedirectForResetPasswordRequest = () => {
    const { history } = this.props
    history.push('/mot-de-passe-perdu?envoye=1')
  }

  submitResetPassword = () => {
    const { submitResetPassword } = this.props
    const { emailValue } = this.state

    return submitResetPassword(
      emailValue,
      this.onHandleSuccessRedirectForResetPasswordRequest,
      this.onHandleFail
    )
  }

  handleInputEmailChange = event => {
    this.setState({ emailValue: event.target.value })
    this.setState({ hasErrorMessage: false })
  }

  render() {
    const { hasErrorMessage, emailValue } = this.state
    const { change, envoye, errors, token } = this.props

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
                    <Form
                      action="/users/new-password"
                      BlockComponent={null}
                      handleSuccessNotification={null}
                      handleSuccessRedirect={this.onHandleSuccessRedirectForResetPassword}
                      layout="vertical"
                      name="user"
                      patch={{ token }}
                    >
                      <Field
                        name="token"
                        storeValue={this.storeValue(token)}
                        type="hidden"
                      />

                      <Field
                        label="Nouveau mot de passe"
                        name="newPassword"
                        placeholder="******"
                        required
                        type="password"
                        value="lolilol"
                      />
                      <div className="errors">
                        {Object.keys(errors).map(field => (
                          <div key={field}>
                            {errors[field].join(' ')}
                          </div>
                        ))}
                      </div>
                      <div className="field buttons-field">
                        <SubmitButton
                          className="primary-button"
                          id="changePassword"
                          type="submit"
                        >
                          {'Envoyer'}
                        </SubmitButton>
                      </div>
                    </Form>
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
                    {hasErrorMessage && (
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
                          type="text"
                          value={emailValue}
                        />
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
  errors: PropTypes.shape().isRequired,
  token: PropTypes.string.isRequired,
}

export default LostPassword
