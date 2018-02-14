import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import FormInput from './FormInput'
import Link from './Link'
import SubmitButton from './SubmitButton'
import { assignData } from '../reducers/data'
import { closeModal } from '../reducers/modal'
import { NEW } from '../utils/config'

const inputClassName = 'input block col-12 mb2'

class Sign extends Component {
  componentWillMount () {
    this.props.assignData({ error: null })
  }
  onSignupClick = () => {
    const { closeModal, history } = this.props
    closeModal()
    history.push('/inscription')
  }
  render () {
    const { error } = this.props
    return (
      <div className='sign'>
        <div className='h1 mb3'>
          Login!
        </div>
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
          path='users/signin'
          storeKey='users'
          text='Connecter' />
        <div className='sign__error mt1'>
          {error && error.message}
        </div>
        <button className='button button--alive' onClick={this.onSignupClick} >
          Pas encore inscrit ?
        </button>
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(
    ({ data, form }) => ({ error: data.error, form }),
    { assignData, closeModal }
  )
)(Sign)
