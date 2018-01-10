import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import { requestData } from '../reducers/request'

const inputClassName = 'input block col-12 mb2'

class Sign extends Component {
  onSubmitClick = () => {
    const { form, requestData } = this.props
    requestData('POST', 'signin', { body: form })
  }
  render () {
    return (
      <div className='sign'>
        <div className='h1 mb3'>
          Login!
        </div>
        <FormInput className={inputClassName}
          name='identifier'
          placeholder='identifiant (CAF ou SIREN)'
        />
        <FormInput className={inputClassName}
          name='password'
          placeholder='password'
          type='password'
        />
        <button className='button button--alive'
          onClick={this.onSubmitClick}
        >
          Connect
        </button>
      </div>
    )
  }
}

export default connect(({ form }) => ({ form }), { requestData })(Sign)
