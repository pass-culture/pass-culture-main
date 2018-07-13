import get from 'lodash.get'
import React from 'react'
import { NavLink } from 'react-router-dom'

import PageWrapper from '../layout/PageWrapper'
import FormField from '../layout/FormField'
import Logo from '../layout/Logo'
import SubmitButton from '../layout/SubmitButton'
import withSign from '../hocs/withSign'
import { NEW } from '../../utils/config'

import Form from '../layout/Form'
import Field from '../layout/Field'
import Submit from '../layout/Submit'

const Label = ({ title }) => {
  return <h3>{title}</h3>
}

const SigninPage = ({ errors }) => {
  return (
    <PageWrapper name="sign-in" fullscreen>
      <div className='logo-side'>
        <Logo />
      </div>
      <div className='container'>
        <div className='columns'>
          <div className='column is-offset-6 is-two-fifths'>
            <section className='hero has-text-grey'>
              <div className='hero-body'>
                <h1 className='title is-spaced is-1'>
                  <span className="has-text-weight-bold ">Bienvenue</span>{' '}
                  <span className="has-text-weight-semibold">dans la version bêta</span>
                  <span className="has-text-weight-normal">du Pass Culture pro.</span>
                </h1>
                <h2 className='subtitle is-2'>Et merci de votre participation pour nous aider à l'améliorer !</h2>
                <Form name='sign-in' action='users/signin' storePath='users' layout='sign-in-up'>
                  <Field name='identifier' type='email' label='Adresse e-mail' placeholder="Identifiant (email)" />
                  <Field name='password' autoComplete="current-password" label='Mot de passe' placeholder='Mot de passe' />
                  <div className="errors">{errors}</div>
                  <div className='field buttons-field'>
                    <NavLink to="/inscription" className="button is-secondary">
                      Créer un compte
                    </NavLink>
                    <Submit className="button is-primary is-outlined">Se connecter</Submit>
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

export default withSign(SigninPage)
