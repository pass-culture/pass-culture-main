import React, { Component } from 'react'
import { connect } from 'react-redux'

import { assignForm } from '../reducers/form'

class FormTextarea extends Component {
  onChange = ({ target: { value } }) => {
    const { assignForm, name } = this.props
    assignForm({ [name]: value })
  }
  render () {
    const { className, defaultValue, placeholder, type } = this.props
    return <textarea className={className || 'textarea'}
      defaultValue={defaultValue}
      onChange={this.onChange}
      placeholder={placeholder}
      type={type} />
  }
}

export default connect(null, { assignForm })(FormTextarea)
