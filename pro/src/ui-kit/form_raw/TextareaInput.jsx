import PropTypes from 'prop-types'
import React from 'react'
import Textarea from 'react-autosize-textarea'

import InputError from './Errors/InputError'

const TextareaInput = ({
  countCharacters,
  disabled,
  error,
  label,
  maxLength,
  name,
  onChange,
  onBlur,
  placeholder,
  required,
  rows,
  subLabel,
  value,
}) => {
  const textareaValue = [undefined, null].includes(value) ? '' : value
  return (
    <label className="input-textarea" htmlFor={name}>
      <div className="labels">
        {label}
        {subLabel && <span className="it-sub-label">{subLabel}</span>}
      </div>
      <Textarea
        className={`it-input ${error ? 'error' : ''}`}
        disabled={disabled}
        id={name}
        maxLength={maxLength}
        name={name}
        onBlur={onBlur}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        rows={rows}
        value={textareaValue}
      />
      {error && <InputError name={name}>{error}</InputError>}
      {countCharacters && (
        <span className="it-character-count">
          {`${textareaValue ? textareaValue.length : 0}/${maxLength}`}
        </span>
      )}
    </label>
  )
}

TextareaInput.defaultProps = {
  countCharacters: false,
  disabled: false,
  error: null,
  label: null,
  maxLength: null,
  onBlur: null,
  onChange: null,
  placeholder: '',
  required: false,
  rows: 4,
  subLabel: '',
  value: '',
}

TextareaInput.propTypes = {
  countCharacters: PropTypes.bool,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  label: PropTypes.string,
  maxLength: PropTypes.number,
  name: PropTypes.string.isRequired,
  onBlur: PropTypes.func,
  onChange: PropTypes.func,
  placeholder: PropTypes.string,
  required: PropTypes.bool,
  rows: PropTypes.number,
  subLabel: PropTypes.string,
  value: PropTypes.string,
}

export default TextareaInput
