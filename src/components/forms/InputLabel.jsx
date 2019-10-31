import React from 'react'
import PropTypes from 'prop-types'

const InputLabel = ({ label, required, sublabel }) => (
  <div className="form-label-inner">
    {label}
    {required && <span className="asterisk">
      {'*'}
    </span>}
    {sublabel && <div className="form-sublabel">
      {sublabel}
    </div>}
  </div>
)

InputLabel.defaultProps = {
  required: false,
  sublabel: null,
}

InputLabel.propTypes = {
  label: PropTypes.string.isRequired,
  required: PropTypes.bool,
  sublabel: PropTypes.string,
}

export default InputLabel
