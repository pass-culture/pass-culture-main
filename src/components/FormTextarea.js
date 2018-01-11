import React, { Component } from 'react'
import { connect } from 'react-redux'

import { assignForm } from '../reducers/form'

class FormTextarea extends Component {
  onChange = ({ target: { value } }) => {
    const { assignForm, name, maxLength } = this.props
    if (value.length < maxLength) {
      assignForm({ [name]: value })
    } else {
      console.warn('value reached maxLength')
    }
  }
  render () {
    const { className, defaultValue, placeholder, type, value } = this.props
    return <textarea className={className || 'textarea'}
      onChange={this.onChange}
      placeholder={placeholder}
      type={type}
      value={value || defaultValue} />
  }
}

FormTextarea.defaultProps = {
  maxLength: 200
}

export default connect(
  (state, ownProps) => ({ value: state.form[ownProps.name] }),
  { assignForm }
)(FormTextarea)
