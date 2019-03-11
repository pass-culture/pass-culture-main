/* eslint
react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import { isEmpty } from '../../../utils/strings'

const DEFAULT_REQUIRED_ERROR = 'Ce champs est requis'
const validateRequiredField = value => {
  if (value && !isEmpty(value)) return undefined
  return DEFAULT_REQUIRED_ERROR
}

const CheckBoxField = ({ children, className, name, required }) => {
  const validateFunc =
    required && typeof required === 'function'
      ? required
      : (required && validateRequiredField) || undefined

  return (
    <Field
      name={name}
      type="checkbox"
      validate={validateFunc || undefined}
      render={({ input, meta }) => (
        <p className={`${className}`}>
          <span className={className}>
            <input
              {...input}
              type="checkbox"
              className="input no-background"
              required={!!required}
            />
            {children}
            <FormError meta={meta} />
          </span>
        </p>
      )}
    />
  )
}

CheckBoxField.defaultProps = {
  className: null,
  required: false,
}

CheckBoxField.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  name: PropTypes.string.isRequired,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
}

export default CheckBoxField
