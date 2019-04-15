/* eslint
  react/jsx-one-expression-per-line: 0 */
import classnames from 'classnames'
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'
import {
  composeValidators,
  createParseNumberValue,
} from 'react-final-form-utils'

import FieldError from 'components/layout/form/FieldError'
import validateRequiredField from 'components/layout/form/utils/validateRequiredField'

function getInputValue(inputType, value) {
  if (inputType === 'number' && typeof value === 'string') {
    return ''
  }
  return value || ''
}

export const TextField = ({
  className,
  disabled,
  format,
  id,
  innerClassName,
  label,
  name,
  parse,
  placeholder,
  readOnly,
  renderInner,
  renderValue,
  required,
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
        const inputType = readOnly ? 'text' : type
        const inputValue = getInputValue(inputType, input.value)
        return (
          <div
            className={classnames('field text-field', className, {
              'is-label-aligned': label,
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
                <div
                  className={classnames(
                    'field-inner flex-columns items-center',
                    innerClassName
                  )}>
                  <input
                    {...input}
                    {...inputProps}
                    className={`field-input field-${type}`}
                    disabled={disabled || readOnly}
                    placeholder={readOnly ? '' : placeholder}
                    readOnly={readOnly}
                    required={!!required}
                    type={inputType}
                    value={inputValue}
                  />
                  {renderInner()}
                </div>
                {renderValue()}
              </div>
              <FieldError meta={meta} />
            </div>
            <div />
          </div>
        )
      }}
    />
  )
}

TextField.defaultProps = {
  className: '',
  disabled: false,
  format: null,
  id: null,
  innerClassName: null,
  label: '',
  parse: null,
  placeholder: '',
  readOnly: false,
  renderInner: () => null,
  renderValue: () => null,
  required: false,
  type: 'text',
  validate: null,
}

TextField.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool,
  format: PropTypes.func,
  id: PropTypes.string,
  innerClassName: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  parse: PropTypes.func,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  renderInner: PropTypes.func,
  renderValue: PropTypes.func,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  type: PropTypes.string,
  validate: PropTypes.func,
}

export default TextField
