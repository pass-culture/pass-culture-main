import get from 'lodash.get'
import { Field, Form, SubmitButton } from 'pass-culture-shared'
import React from 'react'
import { NavLink } from 'react-router-dom'

import PageWrapper from '../layout/PageWrapper'

const SignupPage = () => {
  return (
    <PageWrapper name="sign-up" Tag="form">
      <div className="section form-container">
        <h2 className="subtitle is-italic">
          Une minute pour créer un compte, et puis c'est tout !
        </h2>

        <br />
        <Form
          name="user"
          action="/users/signup"
          layout="vertical"
          handleSuccessNotification={null}
          handleSuccessRedirect={() => '/decouverte'}>
          <Field
            autoComplete="name"
            label="Identifiant"
            name="publicName"
            placeholder="Mon nom ou pseudo"
            required
            sublabel="que verront les autres utilisateurs"
            type="text"
          />
          <Field
            autoComplete="email"
            label="Adresse e-mail"
            name="email"
            placeholder="nom@exemple.fr"
            required
            sublabel="pour se connecter et récupérer son mot de passe en cas d'oubli"
            type="email"
          />
          <Field
            autoComplete="new-password"
            label="Mot de passe"
            name="password"
            placeholder="Mon mot de passe"
            required
            sublabel="pour se connecter"
            type="password"
          />
          <Field
            label={
              <h4>
                {' '}
                J'accepte d'être contacté par mail pour donner mon avis sur le{' '}
                <a
                  href="http://passculture.beta.gouv.fr"
                  style={{ textDecoration: 'underline' }}>
                  Pass Culture
                </a>
                .
              </h4>
            }
            name="contact_ok"
            required
            type="checkbox"
          />
        </Form>
      </div>

      <footer>
        <SubmitButton
          action="/users/signup"
          className="button is-primary is-inverted">
          Créer
        </SubmitButton>
        <NavLink to="/connexion" className="button is-secondary">
          J'ai déjà un compte
        </NavLink>
      </footer>
    </PageWrapper>
  )
}

export default SignupPage
