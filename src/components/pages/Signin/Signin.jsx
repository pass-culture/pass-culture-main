import { Field, Form, SubmitButton } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { NavLink, Link } from 'react-router-dom'
import { compose } from 'redux'

import {
  withFrenchQueryRouter,
  withRedirectToOffersWhenAlreadyAuthenticated,
} from '../../hocs'
import Logo from '../../layout/Logo'
import Main from '../../layout/Main'
import { mapApiToBrowser } from '../../../utils/translate'

class Signin extends Component {
  handleSuccessRedirect = (state, action) => {
    const { query } = this.props
    const currentUser = action.datum
    const { hasOffers, hasPhysicalVenues } = currentUser
    const queryParams = query.parse()
    const fromUrl = queryParams[mapApiToBrowser.from]
    if (fromUrl) {
      return decodeURIComponent(fromUrl)
    }
    return hasOffers || hasPhysicalVenues ? '/offres' : '/structures'
  }

  render() {
    const { errors } = this.props

    return (
      <Main name="sign-in" fullscreen>
        <div className="logo-side">
          <Logo noLink signPage />
        </div>
        <div className="container">
          <div className="columns">
            <div className="column is-offset-6 is-two-fifths">
              <section className="has-text-grey">
                <div className="hero-body">
                  <h1 className="title is-spaced is-1">
                    <span className="has-text-weight-bold ">Bienvenue</span>{' '}
                    <span className="has-text-weight-semibold">
                      dans la version bêta
                    </span>
                    <span className="has-text-weight-normal">
                      du Pass Culture pro.
                    </span>
                  </h1>
                  <h2 className="subtitle is-2">
                    Et merci de votre participation pour nous aider à
                    l'améliorer !
                  </h2>
                  <span className="has-text-grey">
                    {' '}
                    <span className="required-legend"> * </span> Champs
                    obligatoires
                  </span>
                  <Form
                    action="/users/signin"
                    BlockComponent={null}
                    layout="vertical"
                    name="user"
                    handleSuccessNotification={null}
                    handleSuccessRedirect={this.handleSuccessRedirect}
                    onEnterKey={event => event.form.onSubmit()}>
                    <div className="field-group">
                      <Field
                        label="Adresse e-mail"
                        name="identifier"
                        placeholder="Identifiant (email)"
                        required
                        type="email"
                      />
                      <Field
                        autoComplete="current-password"
                        label="Mot de passe"
                        name="password"
                        placeholder="Mot de passe"
                        required
                        type="password"
                      />
                      <span>
                        <Link to="/mot-de-passe-perdu" id="lostPasswordLink">
                          Mot de passe égaré ?
                        </Link>
                      </span>
                    </div>
                    <div className="errors">{errors}</div>
                    <div className="field buttons-field">
                      <NavLink
                        to="/inscription"
                        className="button is-secondary">
                        Créer un compte
                      </NavLink>
                      <SubmitButton
                        className="button is-primary is-outlined"
                        id="signin-submit-button">
                        Se connecter
                      </SubmitButton>
                    </div>
                  </Form>
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
  query: PropTypes.object.isRequired,
}

export default compose(
  withRedirectToOffersWhenAlreadyAuthenticated,
  withFrenchQueryRouter
)(Signin)
