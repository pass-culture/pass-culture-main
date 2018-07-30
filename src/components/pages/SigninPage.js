import get from 'lodash.get'
import { Field, Form, SubmitButton } from 'pass-culture-shared'
import React from 'react'
import { NavLink } from 'react-router-dom'

import PageWrapper from '../layout/PageWrapper'

const inputClassName = 'input block col-12 mb2 red'

const SigninPage = () => {
  return (
    <PageWrapper name="sign-in" Tag="form" redBg>
      <div className="section form-container">
        <h1 className="title is-1 is-italic">Bonjour&nbsp;!</h1>
        <h2 className="subtitle is-2 is-italic">
          Identifiez-vous <br />
          pour accéder aux offres.
        </h2>

        <br />
        <Form
          action="/users/signin"
          layout="vertical"
          name="user"
          handleSuccessNotification={null}
          handleSuccessRedirect={() => '/decouverte'}>
          <Field
            autoComplete="email"
            className={inputClassName}
            label="Adresse e-mail:"
            name="identifier"
            placeholder="Identifiant (email)"
            type="email"
          />
          <Field
            autoComplete="current-password"
            className={inputClassName}
            label="Mot de passe"
            name="password"
            placeholder="Mot de passe"
            type="password"
          />
        </Form>
      </div>

      <footer>
        <SubmitButton
          action="/users/signin"
          className="button is-primary is-inverted">
          Connexion
        </SubmitButton>
        <NavLink to="/inscription" className="button is-secondary">
          Inscription
        </NavLink>
      </footer>
    </PageWrapper>
  )
}

export default SigninPage
