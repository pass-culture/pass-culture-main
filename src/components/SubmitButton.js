import React, { Component } from 'react'
import { connect } from 'react-redux'

import { resetForm } from '../reducers/form'
import { requestData } from '../reducers/request'

class SubmitButton extends Component {
  onSubmitClick = () => {
    const { form,
      getBody,
      getOptimistState,
      method,
      onClick,
      path,
      requestData,
      resetForm
    } = this.props
    requestData(method, path, {
      body: (getBody && getBody(form)) || form,
      getOptimistState
    })
    onClick && onClick()
    resetForm()
  }
  render () {
    const { text } = this.props
    return (
      <button className='button button--alive'
        onClick={this.onSubmitClick}
      >
        { text }
      </button>
    )
  }
}

SubmitButton.defaultProps = { getBody: form => form,
  method: 'POST',
  text: 'Soumettre'
}

export default connect(({ form }) => ({ form }),
  { requestData, resetForm })(SubmitButton)
