import PropTypes from 'prop-types'
import React from 'react'

const PopinButton = ({ action, label }) => (
  <button
    className="popin-button"
    key={label}
    onClick={action}
    type="button"
  >
    {label}
  </button>
)

PopinButton.propTypes = {
  action: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
}

export default PopinButton
