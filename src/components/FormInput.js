import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { getFormValue, mergeForm } from '../reducers/form'
import { NEW } from '../utils/config'

class FormInput extends Component {
  onChange = ({ target: { value } }) => {
    const { collectionName, id, mergeForm, name } = this.props
    mergeForm(collectionName, id, name, value)
  }
  render () {
    const { className,
      defaultValue,
      isRequired,
      placeholder,
      type,
      value
    } = this.props
    return (
      <span>
        <input className={className || 'input'}
          onChange={this.onChange}
          placeholder={placeholder}
          type={type}
          value={value || defaultValue || ''} />
        {isRequired && <span className='form-input__required'> (*) </span>}
      </span>
    )
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

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { mergeForm }
)(FormInput)
