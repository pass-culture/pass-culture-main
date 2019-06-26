/* eslint
  react/jsx-one-expression-per-line: 0 */
import classnames from 'classnames'
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'
import {
  composeValidators,
  createParseNumberValue,
} from 'react-final-form-utils'

import FieldErrors from 'components/layout/form/FieldErrors'
import getRequiredValidate from 'components/layout/form/utils/getRequiredValidate'

function getInputValue(inputType, value) {
  const isStringifiedNumber =
    inputType === 'number' && typeof value === 'string'
  if (!value || isStringifiedNumber) {
    return ''
  }
  return value
}

export class TextField extends Component {
  componentDidMount() {
    const { type } = this.props
    if (type === 'number') {
      this.handlePreventEPlusMinusKeypresses()
    }
  }

  handlePreventEPlusMinusKeypresses = () => {
    this.keypressListener = this.inputElement.addEventListener(
      'keypress',
      event => {
        const hasPressedEKeys = event.which === 69 || event.which === 101
        const hasPressedPlusOrMinusAfterNumbers =
          this.inputElement.value && (event.which === 45 || event.which === 43)
        if (hasPressedEKeys || hasPressedPlusOrMinusAfterNumbers) {
          event.preventDefault()
        }
      }
    )
  }

  componentWillUnmount() {
    if (this.keypressListener) {
      this.inputElement.removeEventListener(this.keypressListener)
    }
  }

  render() {
    const {
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
      value,
      ...inputProps
    } = this.props
    return (
      <Field
        format={format}
        name={name}
        validate={composeValidators(validate, getRequiredValidate(required))}
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
                      id={name}
                      {...input}
                      {...inputProps}
                      className={`field-input field-${type}`}
                      disabled={disabled || readOnly}
                      placeholder={readOnly ? '' : placeholder}
                      readOnly={readOnly}
                      ref={_e => {
                        this.inputElement = _e
                      }}
                      required={!!required}
                      type={inputType}
                      value={inputValue}
                    />
                    {renderInner()}
                  </div>
                  {renderValue()}
                </div>
                <FieldErrors meta={meta} />
              </div>
              <div />
            </div>
          )
        }}
      />
    )
  }
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
