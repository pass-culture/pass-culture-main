import get from 'lodash.get'
import React from 'react'
import { NavLink } from 'react-router-dom'

import FormField from '../components/FormField'
import SubmitButton from '../components/SubmitButton'
import withSign from '../hocs/withSign'
import { NEW } from '../utils/config'

const inputClassName = 'input block col-12 mb2 red'

const Label = ({ title }) => {
  return (
    <div className='mb1'>
      {title}
    </div>
  )
}

const SigninPage = ({ errors }) => {
  return (
    <main className='page sign-page signin-page red'>
      <div className='form-container'>
        <div className='mt3'>
          <div className='h1 semibold'>
            Bonjour&nbsp;!
          </div>
          <div className='h2'>
            Identifiez-vous <br/>
            pour accéder aux offres.
          </div>
        </div>
        <form>
          <FormField className={inputClassName}
            type='email'
            collectionName='users'
            label={<Label title='Adresse e-mail:' />}
            name='identifier'
            placeholder='Identifiant (email)'
            autoComplete='email' />
          <FormField className={inputClassName}
            collectionName='users'
            label={<Label title='Mot de passe' />}
            name='password'
            type='password'
            placeholder='Mot de passe'
            autoComplete='current-password' />
        </form>
        <div className='sign__error mt1'>
          {errors}
        </div>
      </div>
      <footer>
        <NavLink to='/inscription'>
          Inscription
        </NavLink>
        <SubmitButton getBody={form => form.usersById[NEW]}
          getIsDisabled={form => !get(form, 'usersById._new_.identifier') ||
            !get(form, 'usersById._new_.password')}
          className='button button--primary'
          path='users/signin'
          storeKey='users'
          text='Connexion' />
      </footer>
    </main>
  )
}

export default withSign(SigninPage)
