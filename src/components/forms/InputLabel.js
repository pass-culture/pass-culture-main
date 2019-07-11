import React from 'react'
import PropTypes from 'prop-types'

const InputLabel = ({ label, required, sublabel }) => (
  <span className="pc-final-form-label">
    <span>{label}</span>
    {required && <span className="pc-final-form-asterisk">{'*'}</span>}
    {sublabel && <span className="sublabel is-block">{sublabel}</span>}
  </span>
)

InputLabel.defaultProps = {
  sublabel: null,
}

InputLabel.propTypes = {
  label: PropTypes.string.isRequired,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]).isRequired,
  sublabel: PropTypes.string,
}

export default InputLabel
