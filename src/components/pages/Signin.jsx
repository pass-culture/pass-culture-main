import { Field, Form, SubmitButton } from 'pass-culture-shared'
import React from 'react'
import { NavLink, Link } from 'react-router-dom'

import Logo from 'components/layout/Logo'
import Main from 'components/layout/Main'

const SigninPage = ({ errors }) => {
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
                  Et merci de votre participation pour nous aider à l'améliorer
                  !
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
                  handleSuccessRedirect={() => '/offres'}>
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
                    <NavLink to="/inscription" className="button is-secondary">
                      Créer un compte
                    </NavLink>
                    <SubmitButton className="button is-primary is-outlined">
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

export default SigninPage
