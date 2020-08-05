import PropTypes from 'prop-types'
import React from 'react'

const onClick = action => () => {
  document.querySelector('.popin-button').disabled = true
  action()
}

const PopinButton = ({ action, label }) => (
  <button
    className="popin-button"
    key={label}
    onClick={onClick(action)}
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
