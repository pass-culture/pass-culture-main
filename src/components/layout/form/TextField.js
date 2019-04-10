/* eslint
  react/jsx-one-expression-per-line: 0 */
import classnames from 'classnames'
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'
import {
  composeValidators,
  config,
  createParseNumberValue,
  createValidateRequiredField,
} from 'react-final-form-utils'

import FieldError from './FieldError'

const validateRequiredField = createValidateRequiredField(
  config.DEFAULT_REQUIRED_ERROR
)

export const TextField = ({
  autoComplete,
  className,
  disabled,
  format,
  id,
  label,
  name,
  parse,
  placeholder,
  readOnly,
  renderInner,
  renderValue,
  required,
  title,
  type,
  validate,
  ...inputProps
}) => {
  const requiredValidate =
    required && typeof required === 'function'
      ? required
      : (required && validateRequiredField) || undefined

  return (
    <Field
      format={format}
      name={name}
      validate={composeValidators(validate, requiredValidate)}
      parse={parse || createParseNumberValue(type)}
      render={({ input, meta }) => {
        let value = input.value
        if (!readOnly && typeof value === 'string') {
          value = ''
        }
        return (
          <div
            className={classnames('field text-field', className, {
              'is-read-only': readOnly,
            })}
            id={id}>
            <label
              htmlFor={name}
              className={classnames('field-label', { empty: !label })}>
              {label && (
                <span>
                  <span>{label}</span>
                  {required && !readOnly && (
                    <span className="field-asterisk">*</span>
                  )}
                </span>
              )}
            </label>
            <div className="field-control">
              <div className="field-value flex-columns items-center">
                <div className="field-inner flex-columns items-center">
                  <input
                    {...input}
                    {...inputProps}
                    autoComplete={autoComplete ? 'on' : 'off'}
                    className={`field-input field-${type}`}
                    disabled={disabled || readOnly}
                    placeholder={readOnly ? '' : placeholder}
                    readOnly={readOnly}
                    required={!!required} // cast to boolean
                    title={title}
                    type={readOnly ? 'text' : type}
                    value={value}
                  />
                  {renderInner()}
                </div>
                {renderValue()}
              </div>
              <FieldError meta={meta} />
            </div>
          </div>
        )
      }}
    />
  )
}

TextField.defaultProps = {
  autoComplete: false,
  className: '',
  disabled: false,
  format: null,
  id: null,
  label: '',
  parse: null,
  placeholder: 'Please enter a value',
  readOnly: false,
  renderInner: () => null,
  renderValue: () => null,
  required: false,
  title: null,
  type: 'text',
  validate: null,
}

TextField.propTypes = {
  autoComplete: PropTypes.bool,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  format: PropTypes.func,
  id: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  parse: PropTypes.func,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  renderInner: PropTypes.func,
  renderValue: PropTypes.func,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  title: PropTypes.string,
  type: PropTypes.string,
  validate: PropTypes.func,
}

export default TextField
