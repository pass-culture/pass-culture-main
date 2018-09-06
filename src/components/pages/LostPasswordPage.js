import { Field, Form, SubmitButton } from 'pass-culture-shared'
import React from 'react'
import { NavLink } from 'react-router-dom'

import Logo from '../layout/Logo'
import Main from '../layout/Main'

const LostPasswordPage = ({ errors }) => {
  return (
    <Main name="sign-in" fullscreen>
      <div className="logo-side">
        <Logo noLink signPage />
      </div>
      <div className="container">
        <div className="columns">
          <div className="column is-offset-6 is-two-fifths">
            <section className="hero has-text-grey">
              <div className="hero-body">
                <h1 className="title is-spaced is-1">
                  <span className="has-text-weight-normal">
                    Mot de passe égaré ?
                  </span>
                </h1>
                <h2 className="subtitle is-2">
                  Indiquez ci-dessous l’adresse e-mail avec laquelle vous avez
                  créé votre compte.
                </h2>
                <span className="has-text-grey">
                  {' '}
                  <span className="required-legend"> * </span> Champs
                  obligatoires
                </span>
                <Form
                  action="post_for_password_token"
                  BlockComponent={null}
                  layout="vertical"
                  name="user"
                  handleSuccessNotification={null}
                  handleSuccessRedirect={() => '/mot-de-passe-perdu/envoye'}>
                  <Field
                    label="Adresse e-mail"
                    name="identifier"
                    placeholder="Identifiant (email)"
                    required
                    type="email"
                  />
                  <div className="errors">{errors}</div>
                  <div className="field buttons-field">
                    <SubmitButton className="button is-primary is-outlined">
                      Envoyer
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

export default LostPasswordPage
