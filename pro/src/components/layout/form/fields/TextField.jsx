/* eslint react/function-component-definition: 0 */
import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { Field } from 'react-final-form'
import {
  composeValidators,
  createParseNumberValue,
} from 'react-final-form-utils'

import FieldErrors from '../FieldErrors'
import getRequiredValidate from '../utils/getRequiredValidate'

function getInputValue(inputType, value) {
  const isStringifiedNumber =
    inputType === 'number' && typeof value === 'string'

  if (isStringifiedNumber) {
    return ''
  }

  return value
}

function TextField(props) {
  const inputType = props.readOnly ? 'text' : props.type
  const stepValue = inputType === 'number' ? props.step : undefined
  return (
    <Field
      format={props.format}
      id={props.name}
      name={props.name}
      parse={props.parse || createParseNumberValue(props.type)}
      validate={composeValidators(
        props.validate,
        getRequiredValidate(props.required, props.type)
      )}
    >
      {({ input, meta }) => (
        <div
          className={classnames('field text-field', props.className, {
            'is-label-aligned': props.label,
            'is-read-only': props.readOnly,
          })}
          id={props.id}
        >
          {props.label && (
            <label className={classnames('field-label')} htmlFor={props.name}>
              <span>
                <span>{props.label}</span>
                {props.required && !props.readOnly && (
                  <span className="field-asterisk">*</span>
                )}
              </span>
            </label>
          )}
          <div className="field-control">
            <div className="field-value flex-columns items-center">
              <div
                className={classnames(
                  'field-inner flex-columns items-center',
                  props.innerClassName
                )}
              >
                <input
                  id={props.name}
                  {...input}
                  autoComplete={props.autoComplete}
                  className={`field-input field-${props.type}`}
                  disabled={props.disabled || props.readOnly}
                  min={props.min}
                  onBlur={props.onBlur}
                  placeholder={props.readOnly ? '' : props.placeholder}
                  readOnly={props.readOnly}
                  required={!!props.required}
                  step={stepValue}
                  title={props.title}
                  type={inputType}
                  value={getInputValue(inputType, input.value)}
                />
                {props.renderInner()}
              </div>
              {props.renderValue()}
            </div>
            <FieldErrors meta={meta} />
          </div>
          <div />
        </div>
      )}
    </Field>
  )
}

TextField.defaultProps = {
  autoComplete: null,
  className: '',
  disabled: false,
  format: null,
  id: null,
  innerClassName: null,
  label: '',
  min: '',
  onBlur: null,
  parse: null,
  placeholder: '',
  readOnly: false,
  renderInner: function () {
    return null
  },
  renderValue: function () {
    return null
  },
  required: false,
  step: 1,
  title: '',
  type: 'text',
  validate: null,
}

TextField.propTypes = {
  autoComplete: PropTypes.string,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  format: PropTypes.func,
  id: PropTypes.string,
  innerClassName: PropTypes.string,
  label: PropTypes.string,
  min: PropTypes.string,
  name: PropTypes.string.isRequired,
  onBlur: PropTypes.func,
  parse: PropTypes.func,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  renderInner: PropTypes.func,
  renderValue: PropTypes.func,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  step: PropTypes.number,
  title: PropTypes.string,
  type: PropTypes.string,
  validate: PropTypes.func,
}

export default TextField
