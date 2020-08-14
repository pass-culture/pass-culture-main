import React from 'react'
import PropTypes from "prop-types"

const PrimaryButton = ({ disabled, id, name, onClick, text, type }) => (
  // eslint-disable-next-line
  <button
    className="primary-button"
    disabled={disabled}
    id={id}
    name={name}
    onClick={onClick}
    type={type}
  >
    {text}
  </button>
)

PrimaryButton.defaultProps = {
  disabled: false,
  id: null,
  name: null,
  onClick: null,
  type: "button"
}

PrimaryButton.propTypes = {
  disabled: PropTypes.bool,
  id: PropTypes.string,
  name: PropTypes.string,
  onClick: PropTypes.func,
  text: PropTypes.string.isRequired,
  type: PropTypes.oneOf(["button", "submit"])
}

export default PrimaryButton
