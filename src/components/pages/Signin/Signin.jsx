import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Link } from 'react-router-dom'

import GenericError from 'components/layout/errors/GenericError'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import TextInputWithIcon from 'components/layout/inputs/TextInputWithIcon/TextInputWithIcon'
import Logo from 'components/layout/Logo'
import Main from 'components/layout/Main'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { redirectLoggedUser } from 'components/router/helpers'

import { UNAVAILABLE_ERROR_PAGE } from '../../../utils/routes'

class Signin extends PureComponent {
  constructor(props) {
    super(props)
    const { currentUser, history } = props
    redirectLoggedUser(history, currentUser)

    this.state = {
      emailValue: '',
      passwordValue: '',
      isPasswordHidden: true,
      hasErrorMessage: false,
    }
  }

  onHandleSuccessRedirect = (state, action) => {
    const { hasOffers } = action.payload.datum || false
    const { hasPhysicalVenues } = action.payload.datum || false
    const hasOffersWithPhysicalVenues = hasOffers && hasPhysicalVenues
    const { history } = this.props

    const newRoute = hasOffersWithPhysicalVenues || hasPhysicalVenues ? '/offres' : '/structures'
    history.push(newRoute)
  }

  onHandleFail = (state, action) => {
    if (action.payload.errors.password || action.payload.errors.identifier) {
      this.setState({ hasErrorMessage: true })
    }
  }

  handleInputEmailChange = event => {
    this.setState({ emailValue: event.target.value })
    this.setState({ hasErrorMessage: false })
  }

  handleInputPasswordChange = event => {
    this.setState({ passwordValue: event.target.value })
    this.setState({ hasErrorMessage: false })
  }

  handleToggleHidden = e => {
    e.preventDefault()
    this.setState(previousState => ({
      isPasswordHidden: !previousState.isPasswordHidden,
    }))
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { submit } = this.props
    const { emailValue, passwordValue } = this.state

    return submit(emailValue, passwordValue, this.onHandleSuccessRedirect, this.onHandleFail)
  }

  render() {
    const { isAccountCreationAvailable } = this.props
    const { isPasswordHidden, emailValue, passwordValue, hasErrorMessage } = this.state
    const isSubmitButtonDisabled = emailValue === '' || passwordValue === ''
    const accountCreationUrl = isAccountCreationAvailable ? '/inscription' : UNAVAILABLE_ERROR_PAGE

    return (
      <Main
        fullscreen
        name="sign-in"
      >
        <PageTitle title="Se connecter" />
        <div className="logo-side">
          <Logo
            noLink
            signPage
          />
        </div>
        <div className="container">
          <div className="columns">
            <div className="column is-offset-6 is-two-fifths sign-page-form">
              <section>
                <div className="text-container">
                  <h1>
                    {'Bienvenue sur l’espace dédié aux acteurs culturels'}
                  </h1>
                  <h2>
                    {'Et merci de votre participation pour nous aider à l’améliorer !'}
                  </h2>
                  <span className="has-text-grey">
                    {'Tous les champs sont obligatoires'}
                  </span>
                  {hasErrorMessage && (
                    <GenericError message="Identifiant ou mot de passe incorrect." />
                  )}
                  <form
                    noValidate
                    onSubmit={this.handleOnSubmit}
                  >
                    <div className="signin-form">
                      <TextInput
                        label="Adresse e-mail"
                        name="identifier"
                        onChange={this.handleInputEmailChange}
                        placeholder="Identifiant (e-mail)"
                        required
                        type="email"
                        value={emailValue}
                      />
                      <TextInputWithIcon
                        icon={isPasswordHidden ? 'ico-eye-close' : 'ico-eye-open'}
                        iconAlt={
                          isPasswordHidden ? 'Afficher le mot de passe' : 'Cacher le mot de passe'
                        }
                        label="Mot de passe"
                        name="password"
                        onChange={this.handleInputPasswordChange}
                        onIconClick={this.handleToggleHidden}
                        placeholder="Mot de passe"
                        required
                        type={isPasswordHidden ? 'password' : 'text'}
                        value={passwordValue}
                      />
                      <Link
                        className="tertiary-link"
                        id="lostPasswordLink"
                        to="/mot-de-passe-perdu"
                      >
                        {'Mot de passe égaré ?'}
                      </Link>
                    </div>
                    <div className="field buttons-field">
                      <Link
                        className="secondary-link"
                        to={accountCreationUrl}
                      >
                        {'Créer un compte'}
                      </Link>
                      <button
                        className="primary-button"
                        disabled={isSubmitButtonDisabled}
                        id="signin-submit-button"
                        type="submit"
                      >
                        {'Se connecter'}
                      </button>
                    </div>
                  </form>
                </div>
              </section>
            </div>
          </div>
        </div>
      </Main>
    )
  }
}

Signin.propTypes = {
  history: PropTypes.shape().isRequired,
  isAccountCreationAvailable: PropTypes.bool.isRequired,
  submit: PropTypes.func.isRequired,
}

export default Signin
