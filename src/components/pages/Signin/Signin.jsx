import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Link } from 'react-router-dom'

import Logo from '../../layout/Logo'
import Main from '../../layout/Main'
import Icon from '../../layout/Icon'
import { mapApiToBrowser } from '../../../utils/translate'
import { UNAVAILABLE_ERROR_PAGE } from '../../../utils/routes'

class Signin extends PureComponent {
  constructor(props) {
    super(props)
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
    const { query, history } = this.props
    const queryParams = query.parse()
    const fromUrl = queryParams[mapApiToBrowser.from]

    if (fromUrl) {
      return decodeURIComponent(fromUrl)
    }

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

  handleOnSubmit = () => {
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
                  <h1 className="title is-spaced is-1">
                    <span className="has-text-weight-bold ">
                      {'Bienvenue '}
                    </span>
                    <span className="has-text-weight-semibold">
                      {'dans la version bêta '}
                    </span>
                    <span className="has-text-weight-normal">
                      {'du pass Culture pro.'}
                    </span>
                  </h1>
                  <h2 className="subtitle is-2">
                    {'Et merci de votre participation pour nous aider à l’améliorer !'}
                  </h2>
                  <span className="has-text-grey">
                    <span className="required-legend">
                      {'*'}
                    </span>
                    {'Champs obligatoires'}
                  </span>
                  <form>
                    <div className="field-group">
                      <label className="input-text">
                        {'Adresse e-mail'}
                        <span className="field-asterisk">
                          {'*'}
                        </span>
                        <input
                          className="it-input email-input"
                          name="identifier"
                          onChange={this.handleInputEmailChange}
                          placeholder="Identifiant (e-mail)"
                          required
                          type="email"
                          value={emailValue}
                        />
                      </label>
                      <label className="input-text">
                        {'Mot de passe'}
                        <span className="field-asterisk">
                          {'*'}
                        </span>
                        <div className="it-with-icon-container">
                          <input
                            className="it-input-with-icon"
                            name="password"
                            onChange={this.handleInputPasswordChange}
                            placeholder="Mot de passe"
                            required
                            type={isPasswordHidden ? 'password' : 'text'}
                            value={passwordValue}
                          />
                          <button
                            className="it-icon"
                            onClick={this.handleToggleHidden}
                            type="button"
                          >
                            <Icon
                              alt={
                                isPasswordHidden
                                  ? 'Afficher le mot de passe'
                                  : 'Cacher le mot de passe'
                              }
                              svg={isPasswordHidden ? 'ico-eye close' : 'ico-eye'}
                            />
                          </button>
                        </div>
                      </label>
                      {hasErrorMessage && (
                        <div className="errors">
                          <Icon svg="picto-warning" />
                          {'Identifiant ou mot de passe incorrect.'}
                        </div>
                      )}
                    </div>
                    <span>
                      <Link
                        className="tertiary-link"
                        id="lostPasswordLink"
                        to="/mot-de-passe-perdu"
                      >
                        {'Mot de passe égaré ?'}
                      </Link>
                    </span>
                    <div className="field buttons-field">
                      <Link
                        className="secondary-link"
                        to={accountCreationUrl}
                      >
                        {'Créer un compte'}
                      </Link>
                      <button
                        className="button is-primary"
                        disabled={isSubmitButtonDisabled}
                        id="signin-submit-button"
                        onClick={this.handleOnSubmit}
                        type="button"
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
  query: PropTypes.shape().isRequired,
}

export default Signin
