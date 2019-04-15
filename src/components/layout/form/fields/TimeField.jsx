/* eslint
  react/jsx-one-expression-per-line: 0 */
import classnames from 'classnames'
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'
import { composeValidators } from 'react-final-form-utils'
import ReactTimeInput from 'react-time-input'

import validateRequiredField from 'components/layout/form/utils/validateRequiredField'

export const TimeField = ({
  autoComplete,
  className,
  clearable,
  disabled,
  id,
  label,
  locale,
  name,
  placeholder,
  readOnly,
  renderValue,
  required,
  type,
  validate,
  tz,
  // https://www.npmjs.com/package/react-time-input
  ...ReactTimeInputProps
}) => {
  const requiredValidate =
    required && typeof required === 'function'
      ? required
      : (required && validateRequiredField) || undefined

  return (
    <Field
      name={name}
      validate={composeValidators(validate, requiredValidate)}
      render={({ input, meta }) => {
        return (
          <div
            className={classnames('field time-field', className, {
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
                  {readOnly ? (
                    <input
                      className="field-input field-time"
                      readOnly
                      value={input.value}
                    />
                  ) : (
                    <ReactTimeInput
                      className="field-input field-time"
                      initTime={input.value}
                      {...input}
                      {...ReactTimeInputProps}
                      onTimeChange={time => input.onChange(time)}
                    />
                  )}
                </div>
                {renderValue()}
              </div>
            </div>
          </div>
        )
      }}
    />
  )
}

TimeField.defaultProps = {
  autoComplete: false,
  className: '',
  disabled: false,
  id: null,
  label: '',
  locale: 'fr',
  placeholder: 'Please enter a value',
  readOnly: false,
  renderValue: () => null,
  required: false,
  validate: null,
}

TimeField.propTypes = {
  autoComplete: PropTypes.bool,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  id: PropTypes.string,
  label: PropTypes.string,
  locale: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  renderValue: PropTypes.func,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  validate: PropTypes.func,
}

export default TimeField
