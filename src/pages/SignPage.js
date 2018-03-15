import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'

import FormField from '../components/FormField'
import Sign from '../components/Sign'
import SubmitButton from '../components/SubmitButton'
import { showModal } from '../reducers/modal'
import { NEW } from '../utils/config'

const inputClassName = 'input block col-12 mb2'

class SignPage extends Component {
  componentWillReceiveProps (nextProps) {
    const { errors, history, user } = nextProps
    if (user && !errors) {
      history.push('/decouverte') 
    }
  }
  onSigninClick = () => {
    this.props.showModal(<Sign />, { isCloseButton: false })
  }
  render () {
     const { errors } = this.props
    return (
      <main className='page center col-6 mx-auto mt3'>
        <h2>Inscription au Pass Culture</h2>
        <p>Les champs marqués d&apos;une * sont obligatoires.</p>
        <FormField label='Dans le pass, je veux apparaître comme:'
                   required='true'
                   collectionName='users'
                   name='publicName'
                   placeholder='prénom, nom ou pseudo'
                   type='text' />
        <FormField label="Adresse email:"
                   className={inputClassName}
                   collectionName='users'
                   required='true'
                   name='email'
                   type='email'
                   placeholder='email' />
        <FormField label='Cet email me servira à m&apos;identifier, et à récupérer mon mot de passe en cas d&apos;oubli.'
                   className={inputClassName}
                   collectionName='users'
                   required='true'
                   name='password'
                   placeholder='mot de passe'
                   type='password' />
        <FormField className={inputClassName}
                   collectionName='users'
                   required='true'
                   name='contact_ok'
                   type='checkbox'
                   value='true'
                   label='Pass Culture est en phase d&apos;expérimentation. En créant mon compte pendant cette phase, j&apos;accèpte d&apos;être contacté par email pour donner mon avis.' />
        <div className='form-global__errors'>{errors}</div>
        <SubmitButton getBody={form => form.usersById[NEW]}
          path='users'
          storeKey='users'
          text='Soumettre' />
        <button className='button button--alive' onClick={this.onSigninClick}>
          Déjà inscrit ?
        </button>
      </main>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({ errors: state.data.errors && state.data.errors['global'], form: state.form, user:state.user }),
    { showModal }
  ))(SignPage)
