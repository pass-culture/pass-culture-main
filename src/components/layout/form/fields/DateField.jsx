/* eslint
  react/jsx-one-expression-per-line: 0 */
import classnames from 'classnames'
import moment from 'moment'
import React from 'react'
import PropTypes from 'prop-types'
import DatePicker from 'react-datepicker'
import { Field } from 'react-final-form'
import { composeValidators } from 'react-final-form-utils'

import Icon from 'components/layout/Icon'
import getRequiredValidate from 'components/layout/form/utils/getRequiredValidate'

const renderReadOnlyInput = ({ name, readOnlyValue }) => (
  <input
    className="field-input field-date"
    name={name}
    readOnly
    value={readOnlyValue}
  />
)

const renderDateInput = DatePickerProps => (
  <div className="flex-columns items-center field-input field-date">
    <DatePicker {...DatePickerProps} />
    <div className="flex-auto" />
    <Icon alt="Horaires" svg="ico-calendar" />
  </div>
)

const createOnDateChange = input => date => {
  const changedValue = date ? date.toISOString() : null
  input.onChange(changedValue)
}

export const DateField = ({
  autoComplete,
  className,
  clearable,
  dateFormat,
  datePickerClassName,
  disabled,
  id,
  label,
  locale,
  name,
  placeholder,
  readOnly,
  renderInner,
  renderValue,
  required,
  timezone,
  type,
  validate,
  // see github.com/Hacker0x01/react-datepicker/blob/master/docs/datepicker.md
  ...DatePickerProps
}) => {
  const inputName = id || name
  const isClearable = !readOnly && clearable
  return (
    <Field
      name={name}
      validate={composeValidators(validate, getRequiredValidate(required))}
      render={({ input, meta }) => {
        let readOnlyValue
        let selected
        if (input.value) {
          selected = moment(input.value)
          if (timezone) {
            selected = selected.tz(timezone)
          }
          readOnlyValue = selected.format(dateFormat)
        }

        const dateInputProps = {
          className: 'date',
          dateFormat,
          id: inputName,
          isClearable,
          locale,
          placeholderText: placeholder,
          shouldCloseOnSelect: true,
          selected,
          ...DatePickerProps,
          ...input,
          onChange: createOnDateChange(input),
          value: readOnlyValue,
        }

        return (
          <div
            className={classnames('field date-field', className, {
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
                  {readOnly
                    ? renderReadOnlyInput({ name, readOnlyValue })
                    : renderDateInput(dateInputProps)}
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

DateField.defaultProps = {
  autoComplete: false,
  className: '',
  clearable: false,
  dateFormat: 'DD/MM/YYYY',
  datePickerClassName: 'date',
  disabled: false,
  id: null,
  label: '',
  locale: 'fr',
  placeholder: 'Please enter a value',
  readOnly: false,
  renderValue: () => null,
  required: false,
  timezone: null,
  validate: null,
}

DateField.propTypes = {
  autoComplete: PropTypes.bool,
  className: PropTypes.string,
  clearable: PropTypes.bool,
  dateFormat: PropTypes.string,
  datePickerClassName: PropTypes.string,
  disabled: PropTypes.bool,
  id: PropTypes.string,
  label: PropTypes.string,
  locale: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  renderValue: PropTypes.func,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  timezone: PropTypes.string,
  validate: PropTypes.func,
}

export default DateField
