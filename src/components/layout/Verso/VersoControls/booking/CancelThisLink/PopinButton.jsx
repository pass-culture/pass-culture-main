import PropTypes from 'prop-types'
import React from 'react'

const PopinButton = ({ label, id, onClick }) => (
  <button
    className="no-background py12 is-bold fs14"
    id={id}
    key={label}
    onClick={onClick}
    type="button"
  >
    {label}
  </button>
)

PopinButton.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
}

export default PopinButton
