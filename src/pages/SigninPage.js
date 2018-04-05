import get from 'lodash.get'
import React from 'react'
import { NavLink } from 'react-router-dom'

import FormField from '../components/FormField'
import SubmitButton from '../components/SubmitButton'
import withSign from '../hocs/withSign'
import { NEW } from '../utils/config'

const inputClassName = 'input block col-12 mb2 red'

const SigninPage = ({ errors }) => {
  return (
    <main className='page sign-page red'>
      <div className='mt3'>
        <div className='h1 mb1 semibold'>
          Bonjour!
        </div>
        <div>
          Identifiez-vous <br/>
          pour accéder aux offres
        </div>
      </div>
      <form className='mb4'>
        <FormField className={inputClassName}
          type='email'
          collectionName='users'
          label='Adresse e-mail:'
          name='identifier'
          placeholder='Identifiant (email)'
          autoComplete='email' />
        <FormField className={inputClassName}
          collectionName='users'
          label='Mot de passe:'
          name='password'
          type='password'
          placeholder='Mot de passe'
          autoComplete='current-password' />
      </form>
      <div className='sign__error mt1'>
        {errors}
      </div>
      <footer>
        <NavLink to='/inscription'>
          Inscription
        </NavLink>
        <SubmitButton getBody={form => form.usersById[NEW]}
          getIsDisabled={form => !form ||
            !form.usersById ||
            !form.usersById[NEW] ||
            !form.usersById[NEW].identifier ||
            !form.usersById[NEW].password
          }
          className='button button--primary'
          path='users/signin'
          storeKey='users'
          text='Connexion' />
      </footer>
    </main>
  )
}

export default withSign(SigninPage)
