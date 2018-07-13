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

import Form from '../layout/Form'
import Field from '../layout/Field'
import Submit from '../layout/Submit'

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
                  Merci de renseigner tous les champs marqués d'un <span className='required-legend'>*</span>.
                </h2>
                <Form
                  name='sign-up'
                  action='/users'
                  layout='sign-in-up'
                  handleSuccess={() => {
                    showNotification({
                      text: 'Le rattachement de la structure a été demandé. Vous allez recevoir la dernière étape d\'inscription par e-mail.',
                      type: 'success'
                    })
                  }}>
                  <Field
                    name='email'
                    label='Adresse e-mail'
                    sublabel="pour se connecter et récupérer son mot de passe en cas d'oubli"
                    placeholder="nom@exemple.fr"
                    required
                  />
                  <Field
                    name='publicName'
                    label='Identifiant'
                    sublabel='vu par les autres utilisateurs'
                    placeholder='Mon nom ou pseudo'
                    autoComplete='name'
                    required
                  />
                  <Field
                    name='password'
                    label='Mot de passe'
                    sublabel='pour se connecter'
                    placeholder="Mon mot de passe"
                    autoComplete="new-password"
                    required
                  />
                  <Field
                    name='siren'
                    label='SIREN'
                    sublabel='de la structure à rattacher'
                    placeholder="123 456 789"
                    fetchedName={sirenName || ''}
                    required
                  />
                  <Field
                    name="newsletter_ok"
                    type="checkbox"
                    label='Je souhaite recevoir les actualités du Pass Culture.'
                  />
                  <Field
                    name="contact_ok"
                    type="checkbox"
                    label="J'accepte d'être contacté par mail pour donner mon avis sur le Pass Culture."
                    required
                  />
                  <div className="errors">{errors}</div>
                  <div className='field buttons-field'>
                    <NavLink to="/connexion" className="button is-secondary">
                      J'ai déjà un compte
                    </NavLink>
                    <Submit className="button is-primary is-outlined">Créer</Submit>
                  </div>
                </Form>
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
      sirenName: get(state, `form.sign-up.data.name`)
    }),
    {
      addBlockers,
      closeNotification,
      removeBlockers,
      showNotification
    }
  )
)(SignupPage)
