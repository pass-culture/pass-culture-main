import PropTypes from 'prop-types'
import React from 'react'

import InputError from '../Errors/InputError'

const TextInput = ({
  countCharacters,
  disabled,
  error,
  extraClassName,
  inputRef,
  label,
  longDescription,
  maxLength,
  name,
  onChange,
  onBlur,
  onKeyDown,
  placeholder,
  required,
  subLabel,
  type,
  value,
}) => (
  <label className={`input-text ${extraClassName}`}>
    <div className="labels">
      {label}
      {subLabel && <span className="it-sub-label">{subLabel}</span>}
    </div>
    {longDescription && <div className="description">{longDescription}</div>}
    <input
      className={`it-input ${error ? 'error' : ''}`}
      disabled={disabled}
      id={name}
      maxLength={maxLength}
      name={name}
      onBlur={onBlur}
      onChange={onChange}
      onKeyDown={onKeyDown}
      placeholder={placeholder}
      ref={inputRef}
      required={required}
      type={type}
      value={value}
    />
    {error && <InputError name={name}>{error}</InputError>}
    {countCharacters && (
      <span className="it-character-count">
        {`${value ? value.length : 0}/${maxLength}`}
      </span>
    )}
  </label>
)

TextInput.defaultProps = {
  countCharacters: false,
  disabled: false,
  error: null,
  extraClassName: '',
  inputRef: null,
  longDescription: null,
  maxLength: null,
  onBlur: null,
  onChange: null,
  onKeyDown: null,
  placeholder: '',
  required: false,
  subLabel: '',
  type: 'text',
  value: '',
}

TextInput.propTypes = {
  countCharacters: PropTypes.bool,
  disabled: PropTypes.bool,
  error: PropTypes.oneOfType([PropTypes.string, PropTypes.shape()]),
  extraClassName: PropTypes.string,
  inputRef: PropTypes.oneOfType([PropTypes.func, PropTypes.shape()]),
  label: PropTypes.string.isRequired,
  longDescription: PropTypes.string,
  maxLength: PropTypes.number,
  name: PropTypes.string.isRequired,
  onBlur: PropTypes.func,
  onChange: PropTypes.func,
  onKeyDown: PropTypes.func,
  placeholder: PropTypes.string,
  required: PropTypes.bool,
  subLabel: PropTypes.string,
  type: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
}

export default TextInput
