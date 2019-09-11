import React, { Component, Fragment } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import { isEmpty } from '../../../utils/strings'

const DEFAULT_REQUIRED_ERROR = 'Ce champ est requis'
const validateRequiredField = value => {
  if (value && !isEmpty(value)) return undefined
  return DEFAULT_REQUIRED_ERROR
}

class CheckBoxField extends Component {
  renderField = ({ input, meta }) => {
    const { children, className, name, required } = this.props

    return (
      <Fragment>
        <label
          className={`pc-final-form-contact ${className}`}
          htmlFor={name}
        >
          <input
            {...input}
            className="input no-background"
            id={name}
            required={required}
            type="checkbox"
          />
          {children}
        </label>
        <FormError meta={meta} />
      </Fragment>
    )
  }

  render() {
    const { name, required } = this.props
    const validateFunc =
      required && typeof required === 'function'
        ? required
        : (required && validateRequiredField) || undefined

    return (
      <Field
        name={name}
        render={this.renderField}
        type="checkbox"
        validate={validateFunc || undefined}
      />
    )
  }
}

CheckBoxField.defaultProps = {
  className: '',
  required: true,
}

CheckBoxField.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  name: PropTypes.string.isRequired,
  required: PropTypes.bool,
}

export default CheckBoxField
