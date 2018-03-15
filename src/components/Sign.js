import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import FormField from './FormField'
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
    const { errors } = this.props
    return (
      <div className='sign'>
        <div className='h1 mb3'>
          Connecte-toi!
        </div>
        <FormField className={inputClassName}
          type='email'
          collectionName='users'
          name='identifier'
          placeholder='identifiant (email)' />
        <FormField className={inputClassName}
          collectionName='users'
          name='password'
          placeholder='password'
          type='password' />
        <SubmitButton getBody={form => form.usersById[NEW]}
          getIsDisabled={form => !form ||
            !form.usersById ||
            !form.usersById[NEW] ||
            !form.usersById[NEW].identifier ||
            !form.usersById[NEW].password
          }
          path='users/signin'
          storeKey='users'
          text='Connecter' />
        <div className='sign__error mt1'>
          {errors}
        </div>
        <button className='button button--inversed absolute bottom-0 right-0 mb2 mr2'
          onClick={this.onSignupClick} >
          Pas encore inscrit ?
        </button>
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(
    ({ data, form }) => ({ errors: data.errors && data.errors.global, form }),
    { assignData, closeModal }
  )
)(Sign)
