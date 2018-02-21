import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormInput from '../components/FormInput'
import Sign from '../components/Sign'
import SubmitButton from '../components/SubmitButton'
import { showModal } from '../reducers/modal'
import { NEW } from '../utils/config'

const inputClassName = 'input block col-12 mb2'

class SignPage extends Component {
  onSigninClick = () => {
    this.props.showModal(<Sign />, { isCloseButton: false })
  }
  render () {
    // const { form } = this.props
    return (
      <main className='page center col-6 mx-auto mt3'>
        <FormInput className={inputClassName}
          collectionName='users'
          name='identifier'
          placeholder='identifiant (email)' />
        <FormInput className={inputClassName}
          collectionName='users'
          name='password'
          placeholder='password'
          type='password' />
        <SubmitButton getBody={form => form.usersById[NEW]}
          path='users/signup'
          storeKey='users'
          text='Soumettre' />
        <button className='button button--alive' onClick={this.onSigninClick}>
          Déjà inscrit ?
        </button>
      </main>
    )
  }
}

export default connect(
  ({ form }) => ({ form }),
  { showModal }
)(SignPage)
