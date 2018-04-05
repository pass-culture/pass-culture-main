import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import FormField from '../components/FormField'
import SubmitButton from '../components/SubmitButton'
import { assignData } from '../reducers/data'
import { NEW } from '../utils/config'

const inputClassName = 'input block col-12 mb2 red'

class SigninPage extends Component {
  componentWillMount () {
    this.props.assignData({ error: null })
  }
  render () {
    const { errors } = this.props
    return (
      <main className='page sign-page red'>
        <div>
          <div className='h1 mb1'>
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
}

export default connect(
  ({ data, form }) => ({
    errors: data.errors && data.errors.global,
    form
  }),
  { assignData }
)(SigninPage)
