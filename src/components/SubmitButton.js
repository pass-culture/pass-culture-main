import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { resetForm } from '../reducers/form'
import { requestData } from '../reducers/data'

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
    const { className, getIsDisabled, form, text } = this.props
    console.log('getIsDisabled(form)', getIsDisabled(form), form)
    const isDisabled = getIsDisabled(form)
    return (
      <button className={classnames(className || 'button button--alive button--cta', {
          'button--disabled': isDisabled
        })}
        disabled={isDisabled}
        onClick={this.onSubmitClick}
      >
        { text }
      </button>
    )
  }
}

SubmitButton.defaultProps = { getBody: form => form,
  getIsDisabled: form => Object.keys(form).length === 0,
  method: 'POST',
  text: 'Soumettre'
}

SubmitButton.propTypes = {
  path: PropTypes.string.isRequired
}

export default connect(({ form }) => ({ form }),
  { requestData, resetForm })(SubmitButton)
