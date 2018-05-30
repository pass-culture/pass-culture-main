import get from 'lodash.get'
import React from 'react'
import { NavLink } from 'react-router-dom'

import PageWrapper from '../layout/PageWrapper'
import FormField from '../layout/FormField'
import Logo from '../layout/Logo'
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
    <PageWrapper name="sign-up" noHeader noContainer>
      <div className='columns'>
        <div className='column is-one-quarter logo-column'>
          <Logo />
        </div>
        <div className='column is-one-quarter has-text-grey has-big-margin'>
          <section className='hero'>
            <div className='hero-body'>
              <h1 className='title is-spaced is-1'>Créez votre compte</h1>
              <p className='subtitle'>Merci de renseigner tous les champs suivants pour créer votre compte.</p>
            </div>
          </section>
        </div>
        <div className='column is-one-quarter has-big-margin'>
          <form>
            {false && (
              <FormField
                className="input is-rounded"
                label={
                  <Label
                    title="SIREN"
                    subtitle="... qui rend mon compte unique :"
                  />
                }
                required
                collectionName="users"
                name="siren"
                autoComplete="siren"
                placeholder="SIREN"
                type="text"
              />
            )}
            <FormField
              className="input is-rounded"
              label={
                <Label
                  title="Adresse e-mail"
                  subtitle="... pour se connecter et récupérer son mot de passe en cas d'oubli :"
                />
              }
              collectionName="users"
              required
              autoComplete="email"
              name="email"
              type="email"
              placeholder="nom@exemple.fr"
            />
            <FormField
              className="input is-rounded"
              label={
                <Label
                  title="Identifiant"
                  subtitle="... vu par les autres utilisateurs :"
                />
              }
              required
              collectionName="users"
              name="publicName"
              autoComplete="name"
              placeholder="Mon nom ou pseudo"
              type="text"
            />
            <FormField
              className="input is-rounded"
              label={
                <Label
                  title="Mot de passe"
                  subtitle="... pour se connecter :"
                />
              }
              collectionName="users"
              required
              autoComplete="new-password"
              name="password"
              placeholder="Mon mot de passe"
              type="password"
            />
            <FormField
              label={
                <span>
                  J'accepte d'être contacté par mail pour donner mon avis sur le{' '}
                  <a href="http://passculture.beta.gouv.fr">Pass Culture</a>.
                </span>
              }
              collectionName="users"
              required
              name="contact_ok"
              type="checkbox"
            />
            <div className="errors">{errors}</div>
            <div className='field buttons-field'>
              <NavLink to="/connexion" className="button is-secondary">
                J'ai déjà un compte
              </NavLink>
              <SubmitButton
                text="Créer"
                className="button is-primary is-outlined"
                getBody={form => form.usersById[NEW]}
                getIsDisabled={form =>
                  !get(form, 'usersById._new_.publicName') ||
                  !get(form, 'usersById._new_.email') ||
                  !get(form, 'usersById._new_.password')
                }
                path="users"
                storeKey="users"
              />
            </div>
          </form>

        </div>
      </div>
    </PageWrapper>
  )
}

export default withSign(SignupPage)
