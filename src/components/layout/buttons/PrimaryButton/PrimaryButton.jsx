import React from 'react'
import PropTypes from "prop-types"

const PrimaryButton = ({ disabled, id, name, text, type }) => (
  <button
    className="primary-button"
    disabled={disabled}
    id={id}
    name={name}
    type={type}
  >
    {text}
  </button>
)

PrimaryButton.defaultProps = {
  disabled: false,
  id: null,
  name: null,
  type: "button"
}

PrimaryButton.propTypes = {
  disabled: PropTypes.bool,
  id: PropTypes.string,
  name: PropTypes.string,
  text: PropTypes.string.isRequired,
  type: PropTypes.oneOf(["button", "submit"])
}

export default PrimaryButton
