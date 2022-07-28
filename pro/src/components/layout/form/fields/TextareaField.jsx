import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import Textarea from 'react-autosize-textarea'
import { Field } from 'react-final-form'

import { composeValidators } from 'utils/react-final-form'

import FieldErrors from '../FieldErrors'
/*eslint no-undef: 0*/

import getRequiredValidate from '../utils/getRequiredValidate'

function formatInputValueIfTooLong(value, maxLength) {
  const valueLength = value.length
  const valueIsTooLong = valueLength > maxLength - 1
  return valueIsTooLong ? value.slice(0, maxLength - 1) : value
}

class TextareaField extends PureComponent {
  renderField = ({ input, meta }) => {
    const {
      autoComplete,
      className,
      disabled,
      label,
      maxLength,
      name,
      placeholder,
      readOnly,
      required,
      rows,
    } = this.props

    // for a deeper usage of react-autosize-textarea
    // see https://github.com/buildo/react-autosize-textarea
    const autosizeTextareaProps = { rows }
    const value = formatInputValueIfTooLong(input.value, maxLength)

    return (
      <div
        className={classnames('field textarea-field', className, {
          'is-label-aligned': label,
          'is-read-only': readOnly,
        })}
      >
        <label
          className={classnames('field-label', { empty: !label })}
          htmlFor={name}
        >
          {label && (
            <span>
              <span>{label}</span>
              {required && !readOnly && (
                <span className="field-asterisk">*</span>
              )}
              {!readOnly && (
                <Fragment>
                  <br />
                  <span className="character-count">
                    {` (${input.value.length} / ${maxLength}) `}
                  </span>
                </Fragment>
              )}
            </span>
          )}
        </label>
        <div className="field-control">
          <div className="field-value flex-columns items-center">
            <span className="field-inner">
              <Textarea
                {...input}
                autoComplete={autoComplete ? 'on' : 'off'}
                className="field-textarea"
                disabled={disabled || readOnly}
                id={name}
                placeholder={readOnly ? '' : placeholder}
                readOnly={readOnly}
                required={!!required}
                value={value}
                {...autosizeTextareaProps}
              />
            </span>
          </div>
          <FieldErrors meta={meta} />
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

TextareaField.defaultProps = {
  autoComplete: false,
  className: '',
  disabled: false,
  label: '',
  maxLength: 1000,
  placeholder: '',
  readOnly: false,
  required: false,
  rows: null,
  validate: null,
}

TextareaField.propTypes = {
  autoComplete: PropTypes.bool,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  label: PropTypes.string,
  maxLength: PropTypes.number,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  rows: PropTypes.number,
  validate: PropTypes.func,
}

export default TextareaField
