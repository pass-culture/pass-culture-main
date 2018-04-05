import get from 'lodash.get'
import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'

import FormField from '../components/FormField'
import Sign from '../components/Sign'
import SubmitButton from '../components/SubmitButton'
import { showModal } from '../reducers/modal'
import { NEW } from '../utils/config'

class SignupPage extends Component {
  componentWillReceiveProps (nextProps) {
    const { errors, history, user } = nextProps
    if (user && !errors) {
      history.push('/decouverte')
    }
  }
  onSigninClick = () => {

  }
  render () {
    const {
      showModal,
      errors,
    } = this.props
    return (
      <main className='page sign-page'>
        <p>Une minute pour créer un compte, et puis c'est tout !</p>
        <FormField label={<span>Nom ou pseudo : <small>(c'est lui que verront les autres utilisateurs)</small></span>}
                   required='true'
                   collectionName='users'
                   name='publicName'
                   autoComplete='name'
                   placeholder='Rosa'
                   type='text' />
        <FormField label={<span>Adresse email : <small>(pour se connecter et récupérer son mot de passe en cas d'oubli)</small></span>}
                   collectionName='users'
                   required='true'
                   autoComplete='email'
                   name='email'
                   type='email'
                   placeholder='rose@domaine.fr' />
        <FormField label={<span>Mot de passe : <small>(pour se connecter)</small></span>}
                   collectionName='users'
                   required='true'
                   autoComplete='new-password'
                   name='password'
                   placeholder='mot de passe'
                   type='password' />
        <div className='errors'>{errors}</div>
        <footer>
          <button className='button button--secondary' onClick={e => showModal(<Sign />)}>
            Déjà inscrit ?
          </button>
          <SubmitButton
            text='OK'
            className='button button--secondary'
            getBody={form => form.usersById[NEW]}
            getIsDisabled={form => !get(form, 'usersById._new_.publicName') || !get(form, 'usersById._new_.email') || !get(form, 'usersById._new_.password')}
            path='users'
            storeKey='users' />
        </footer>
      </main>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({
      errors: state.data.errors && state.data.errors['global'],
      form: state.form, user:state.user
    }),
    { showModal }
  ))(SignupPage)
