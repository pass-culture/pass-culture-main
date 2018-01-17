import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import SubmitButton from './SubmitButton'
import { requestData } from '../reducers/data'
import { NEW } from '../utils/config'

const inputClassName = 'input block col-12 mb2'

class Sign extends Component {
  onSubmitClick = () => {
    const { form, requestData } = this.props
    requestData('POST', 'signin', { body: form, key: 'user' })
  }
  render () {
    return (
      <div className='sign'>
        <div className='h1 mb3'>
          Login!
        </div>
        <FormInput className={inputClassName}
          collectionName='users'
          name='identifier'
          placeholder='identifiant (CAF ou SIREN)'
        />
        <FormInput className={inputClassName}
          collectionName='users'
          name='password'
          placeholder='password'
          type='password'
        />
        <SubmitButton getBody={form => form.usersById[NEW]}
          path='signin'
          text='Connecter'
        />
      </div>
    )
  }
}

export default connect(({ form }) => ({ form }), { requestData })(Sign)
