import get from 'lodash.get'
import React from 'react'
import { NavLink } from 'react-router-dom'

import PageWrapper from '../layout/PageWrapper'
import FormField from '../layout/FormField'
import SubmitButton from '../layout/SubmitButton'
import withSign from '../hocs/withSign'
import { NEW } from '../../utils/config'

const Label = ({ subtitle, title, inline }) => (
  <div className={inline && 'inline'}>
    <h3>{title}</h3>
    <p>{subtitle}</p>
  </div>
)

const SignupPage = ({ errors }) => {
  return (
    <PageWrapper name="sign-up" Tag="form">
      <div className="form-container">
        <FormField
          className="input"
          label={
            <Label
              title="SIREN"
            />
          }
          required="true"
          collectionName="users"
          name="siren"
          autoComplete="siren"
          placeholder="SIREN"
          type="text"
        />
        <FormField
          className="input"
          label={
            <Label
              title="Identifiant"
            />
          }
          required="true"
          collectionName="users"
          name="publicName"
          autoComplete="name"
          placeholder="Mon nom ou pseudo"
          type="text"
        />
        <FormField
          className="input"
          label={
            <Label
              title="Adresse e-mail"
            />
          }
          collectionName="users"
          required="true"
          autoComplete="email"
          name="email"
          type="email"
          placeholder="nom@exemple.fr"
        />
        <FormField
          className="input"
          label={
            <Label
              title="Mot de passe"
              inline
            />
          }
          collectionName="users"
          required="true"
          autoComplete="new-password"
          name="password"
          placeholder="Mon mot de passe"
          type="password"
        />
        <FormField
          label={
            <h4>
              {' '}
              J'accepte d'être contacté par mail pour donner mon avis sur le{' '}
              <a href="http://passculture.beta.gouv.fr">Pass Culture</a>.
            </h4>
          }
          collectionName="users"
          required="true"
          name="contact_ok"
          type="checkbox"
        />
        <div className="errors">{errors}</div>
      </div>
      <footer>
        <SubmitButton
          text="Créer"
          className="button is-primary is-inverted"
          getBody={form => form.usersById[NEW]}
          getIsDisabled={form =>
            !get(form, 'usersById._new_.publicName') ||
            !get(form, 'usersById._new_.email') ||
            !get(form, 'usersById._new_.password')
          }
          path="users"
          storeKey="users"
        />
        <NavLink to="/connexion" className="button is-secondary">
          J'ai déjà un compte
        </NavLink>
      </footer>
    </PageWrapper>
  )
}

export default withSign(SignupPage)
