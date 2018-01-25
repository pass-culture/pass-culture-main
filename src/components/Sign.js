import React from 'react'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import SubmitButton from './SubmitButton'
import { requestData } from '../reducers/data'
import { NEW } from '../utils/config'

const inputClassName = 'input block col-12 mb2'

const Sign = ({
  error
}) => {
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
    </div>
  )
}

export default connect(
  ({ data, form }) => ({ error: data.error, form }),
  { requestData }
)(Sign)
