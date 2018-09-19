/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

export const InputField = ({
  defaultValue,
  disabled,
  label,
  name,
  placeholder,
}) => (
  <Field
    name={name}
    defaultValue={defaultValue}
    render={({ input, meta }) => (
      <p className="fs19">
        <label htmlFor={name} className="pc-form-label">
          {label && <span className="is-block">{label}</span>}
          <input
            id={name}
            type="text"
            disabled={disabled}
            className="is-block"
            onChange={input.onChange}
            placeholder={placeholder}
            defaultValue={defaultValue}
          />
        </label>
        {meta.error && meta.touched && <span>{meta.error}</span>}
      </p>
    )}
  />
)
InputField.defaultProps = {
  defaultValue: '',
  disabled: false,
  label: PropTypes.string,
  placeholder: 'Veuillez saisir une valeur',
}

InputField.propTypes = {
  defaultValue: PropTypes.string,
  disabled: PropTypes.bool,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
}

export default InputField
