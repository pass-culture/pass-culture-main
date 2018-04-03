import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/data'

class SubmitButton extends Component {

  onSubmitClick = event => {
    event.preventDefault();
    const {
      add,
      form,
      getBody,
      getOptimistState,
      getSuccessState,
      method,
      onClick,
      path,
      storeKey,
      requestData
    } = this.props;
    requestData(method, path, { add,
      body: (getBody && getBody(form)) || form,
      getOptimistState,
      getSuccessState,
      key: storeKey
    })
    onClick && onClick()
  }

  render() {
    const { className, extraClass, getIsDisabled, form, text } = this.props
    const isDisabled = getIsDisabled(form)
    return (
      <button className={classnames(className || 'button button--alive button--cta', {
          'button--disabled': isDisabled,
          [extraClass]: extraClass
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
  { requestData })(SubmitButton)
