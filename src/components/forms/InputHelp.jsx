import React from 'react'
import PropTypes from 'prop-types'

const InputHelp = ({ label }) => (
  <span className="pc-final-form-help">
    <span>{label}</span>
  </span>
)

InputHelp.propTypes = {
  label: PropTypes.string.isRequired,
}

export default InputHelp
