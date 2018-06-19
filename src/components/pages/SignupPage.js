import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import PageWrapper from '../layout/PageWrapper'
import FormField from '../layout/FormField'
import Logo from '../layout/Logo'
import SubmitButton from '../layout/SubmitButton'
import withSign from '../hocs/withSign'
import { addBlockers, removeBlockers } from '../../reducers/blockers'
import { closeNotification, showNotification } from '../../reducers/notification'
import { NEW } from '../../utils/config'

const Label = ({ subtitle, title, inline }) => (
  <div className={inline && 'inline'}>
    <h3 className='can-be-required'>{title}</h3>
    <p>{subtitle}</p>
  </div>
)

const requiredFields = [
  'address',
  'contact_ok',
  'email',
  'latitude',
  'longitude',
  'name',
  'password',
  'postalCode',
  'publicName',
  'siren'
]

const SignupPage = ({
  addBlockers,
  closeNotification,
  errors,
  removeBlockers,
  showNotification
}) => {
  return (
    <PageWrapper name="sign-up" fullscreen>
      <div className='columns'>
        <div className='column is-half logo-column'>
          <Logo />
        </div>
        <div className='column is-one-third has-big-margin'>
          <section className='hero'>
            <div className='hero-body has-text-grey'>
              <h1 className='title is-spaced is-1'>Créez votre compte</h1>
              <p className='subtitle'>
                Merci de renseigner tous les champs suivants pour créer votre compte.
              </p>
              <form>
                <FormField
                  autoComplete="email"
                  collectionName="users"
                  inputClassName="input is-rounded"
                  label={
                    <Label
                      title="Adresse e-mail"
                      subtitle="... pour se connecter et récupérer son mot de passe en cas d'oubli :"
                    />
                  }
                  name="email"
                  placeholder="nom@exemple.fr"
                  required
                  type="email"
                />
                <FormField
                  inputClassName="input is-rounded"
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
                  autoComplete="new-password"
                  collectionName="users"
                  inputClassName="input is-rounded"
                  label={
                    <Label
                      title="Mot de passe"
                      subtitle="... pour se connecter :"
                    />
                  }
                  name="password"
                  placeholder="Mon mot de passe"
                  required
                  type="password"
                />
                <FormField
                  autoComplete="siren"
                  collectionName="users"
                  inputClassName="input is-rounded"
                  required
                  label={
                    <Label
                      title="Siren"
                      subtitle="... de la structure à rattacher :"
                    />
                  }
                  name="siren"
                  placeholder="123 456 789"
                  sireType="siren"
                  type="sirene"
                />
                <FormField
                  collectionName="users"
                  label={
                    <span>
                      J'accepte d'être contacté par mail pour donner mon avis sur le{' '}
                      <a href="http://passculture.beta.gouv.fr">Pass Culture</a>.
                    </span>
                  }
                  name="contact_ok"
                  required
                  type="checkbox"
                />
                <div className="errors">{errors}</div>
                <div className='field buttons-field'>
                  <NavLink to="/connexion" className="button is-secondary">
                    J'ai déjà un compte
                  </NavLink>
                  <SubmitButton
                    className="button is-primary is-outlined"
                    getBody={form => form.usersById[NEW]}
                    getIsDisabled={form =>
                      requiredFields.filter(k =>
                        !get(form, `usersById._new_.${k}`)
                      ).length > 0
                    }
                    handleSuccess={() => {
                      addBlockers(
                        'signup-offerer-notification',
                        ({ location: { pathname }}) => {
                          if (pathname === '/structures') {
                            removeBlockers('signup-offerer-notification')
                            closeNotification()
                          }
                        }
                      )
                      showNotification({
                        text: 'Le rattachement de la structure a été demandé. Vous allez recevoir la dernière étape d\'inscription par e-mail.',
                        type: 'success'
                      })
                    }}
                    path="users"
                    storeKey="users"
                    text="Valider"
                  />
                </div>
              </form>
            </div>
          </section>

        </div>
      </div>
    </PageWrapper>
  )
}

export default compose(
  withSign,
  connect(
    null,
    {
      addBlockers,
      closeNotification,
      removeBlockers,
      showNotification
    }
  )
)(SignupPage)
