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
    <h3 className={`can-be-required ${subtitle ? 'with-subtitle' : ''}`}>{title}</h3>
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
  sirenName,
  showNotification
}) => {
  return (
    <PageWrapper name="sign-up" fullscreen>
      <div className='logo-side'>
        <Logo />
      </div>
      <div className='container'>
        <div className='columns'>
          <div className='column is-offset-6 is-two-fifths'>
            <section className='hero'>
              <div className='hero-body'>
                <h1 className='title is-spaced is-1'>Créez votre compte</h1>
                <h2 className='subtitle is-2'>
                  Merci de renseigner tous les champs suivants pour créer votre compte.
                </h2>
                <form>
                  <FormField
                    autoComplete="email"
                    collectionName="users"
                    inputClassName="input"
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
                    inputClassName="input"
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
                    inputClassName="input"
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
                    inputClassName="input"
                    label={
                      <Label
                        title="SIREN"
                        subtitle="... de la structure à rattacher :"
                      />
                    }
                    name="siren"
                    placeholder="123 456 789"
                    required
                    sireType="siren"
                    type="sirene"
                    withDisplayName
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
                          !get(form, `usersById.${NEW}.${k}`)
                        ).length > 0
                      }
                      handleSuccess={() => {
                        showNotification({
                          text: 'Le rattachement de la structure a été demandé. Vous allez recevoir la dernière étape d\'inscription par e-mail.',
                          type: 'success'
                        })
                      }}
                      path="users"
                      storeKey="users"
                      text="Créer"
                    />
                  </div>
                </form>
              </div>
            </section>

          </div>
        </div>
      </div>
    </PageWrapper>
  )
}

export default compose(
  withSign,
  connect(
    state => ({
      sirenName: get(state, `form.usersById.${NEW}.name`)
    }),
    {
      addBlockers,
      closeNotification,
      removeBlockers,
      showNotification
    }
  )
)(SignupPage)
