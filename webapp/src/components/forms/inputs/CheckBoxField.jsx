import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import isEmpty from '../../../utils/strings/isEmpty'

const DEFAULT_REQUIRED_ERROR = 'Ce champ est requis'
const validateRequiredField = value => {
  if (value && !isEmpty(value)) return undefined
  return DEFAULT_REQUIRED_ERROR
}

class CheckBoxField extends PureComponent {
  renderField = ({ input, meta }) => {
    const { children, name, required } = this.props

    return (
      <Fragment>
        <label className="label-contact-inner">
          <span>
            <input
              {...input}
              className="input form-checkbox"
              id={name}
              required={required}
              type="checkbox"
            />
          </span>
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
  required: true,
}

CheckBoxField.propTypes = {
  children: PropTypes.node.isRequired,
  name: PropTypes.string.isRequired,
  required: PropTypes.bool,
}

export default CheckBoxField
