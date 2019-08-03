import PropTypes from 'prop-types'
import React from 'react'

const PopinButton = ({ label, id, onClick }) => (
  <button
    className="no-border no-background no-outline is-block py12 is-bold fs14"
    id={id}
    key={label}
    onClick={onClick}
    type="button"
  >
    <span>{label}</span>
  </button>
)

PopinButton.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired
}

export default PopinButton
