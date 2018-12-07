/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

const InputLabel = ({ label, required }) => (
  <span className="pc-final-form-label">
    <span>{label}</span>
    {required && <span className="pc-final-form-asterisk">*</span>}
  </span>
)

InputLabel.propTypes = {
  label: PropTypes.string.isRequired,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]).isRequired,
}

export default InputLabel
