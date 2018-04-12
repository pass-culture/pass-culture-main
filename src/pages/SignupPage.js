import classnames from 'classnames'
import get from 'lodash.get'
import React from 'react'
import { NavLink } from 'react-router-dom'

import FormField from '../components/FormField'
import SubmitButton from '../components/SubmitButton'
import withSign from '../hocs/withSign'
import { NEW } from '../utils/config'

const Label = ({ isJumpLine, subtitle, title }) => (
  <div className={classnames('mb1', {
    'left left-align': isJumpLine,
    'flex col-12 items-baseline': !isJumpLine
  })}>
    <span className='h3 mr3'> {title} </span> {isJumpLine && <br/>}
    { !isJumpLine && <div className='flex-auto' /> }
    <span className='h4'> {subtitle} </span>
  </div>
)


const SignupPage = ({ errors }) => {
  return (
    <main className='page sign-page'>
      <div className='form-container'>
        <p className='h2-black'>Une minute pour créer un compte, et puis c'est tout !</p>
        <form>
          <FormField className='input'
                     label={
                       <Label isJumpLine
                              title='Identifiant'
                              subtitle='...que verront les autres utilisateurs:' />
                     }
                     required='true'
                     collectionName='users'
                     name='publicName'
                     autoComplete='name'
                     placeholder='Mon nom ou pseudo'
                     type='text' />
          <FormField className='input'
                     label={
                       <Label isJumpLine
                              title='Adresse e-mail'
                              subtitle="...pour se connecter et récupérer son mot de passe en cas d'oubli:" />
                     }
                     collectionName='users'
                     required='true'
                     autoComplete='email'
                     name='email'
                     type='email'
                     placeholder='nom@exemple.fr' />
          <FormField className='input'
                     label={
                       <Label title='Mot de passe'
                              subtitle="...pour se connecter:" />
                     }
                     collectionName='users'
                     required='true'
                     autoComplete='new-password'
                     name='password'
                     placeholder='Mon mot de passe'
                     type='password' />
          <FormField label={<span className="h4"> J'accepte d'être contacté par mail pour donner mon avis sur le <a href="http://passculture.beta.gouv.fr">Pass Culture</a>.</span>}
                     collectionName='users'
                     required='true'
                     name='contact_ok'
                     type='checkbox' />
        </form>
        <div className='errors'>{errors}</div>
      </div>
      <footer className='flex items-center'>
        <NavLink to='/connexion'>
          J'ai déjà un compte
        </NavLink>
        <SubmitButton
          text='Créer'
          className='button button--primary'
          getBody={form => form.usersById[NEW]}
          getIsDisabled={form => !get(form, 'usersById._new_.publicName') ||
            !get(form, 'usersById._new_.email') ||
            !get(form, 'usersById._new_.password')}
          path='users'
          storeKey='users' />
      </footer>
    </main>
  )
}

export default withSign(SignupPage)
