import classnames from 'classnames'
import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'
import { composeValidators } from 'react-final-form-utils'
import ReactTimeInput from 'react-time-input'

import getRequiredValidate from '../utils/getRequiredValidate'

class TimeField extends PureComponent {
  handleOnTimeChange = input => time => input.onChange(time)

  renderField = ({ input }) => {
    const {
      className,
      id,
      label,
      name,
      readOnly,
      renderValue,
      required,
      // see https://www.npmjs.com/package/react-time-input
      ...ReactTimeInputProps
    } = this.props

    return (
      <div
        className={classnames('field time-field', className, {
          'is-read-only': readOnly,
        })}
        id={id}
      >
        <label
          className={classnames('field-label', { empty: !label })}
          htmlFor={name}
        >
          {label && (
            <span>
              <span>{label}</span>
              {required && !readOnly && <span className="field-asterisk">{'*'}</span>}
            </span>
          )}
        </label>
        <div className="field-control">
          <div className="field-value flex-columns items-center">
            <div className="field-inner flex-columns items-center">
              {readOnly ? (
                <input
                  className="field-input field-time"
                  name={name}
                  readOnly
                  value={input.value}
                />
              ) : (
                <ReactTimeInput
                  className="field-input field-time"
                  initTime={input.value}
                  {...input}
                  {...ReactTimeInputProps}
                  onTimeChange={this.handleOnTimeChange(input)}
                />
              )}
            </div>
            {renderValue()}
          </div>
        </div>
      </div>
    )
  }

  render() {
    const { name, required, validate } = this.props

    return (
      <Field
        name={name}
        render={this.renderField}
        validate={composeValidators(validate, getRequiredValidate(required))}
      />
    )
  }
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
