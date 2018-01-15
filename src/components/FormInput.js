import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { mergeForm } from '../reducers/form'
import { NEW } from '../utils/config'

class FormInput extends Component {
  onChange = ({ target: { value } }) => {
    const { collectionName, id, mergeForm, name } = this.props
    mergeForm(collectionName, id, name, value)
  }
  render () {
    const { className, defaultValue, isRequired, placeholder, type } = this.props
    return <input className={className || 'input'}
      defaultValue={defaultValue}
      onChange={this.onChange}
      placeholder={placeholder}
      required={isRequired}
      type={type} />
  }
}

FormInput.defaultProps = {
  id: NEW
}

FormInput.propTypes = {
  collectionName: PropTypes.string.isRequired,
  id: PropTypes.string,
  name: PropTypes.string.isRequired
}

export default connect(null, { mergeForm })(FormInput)
