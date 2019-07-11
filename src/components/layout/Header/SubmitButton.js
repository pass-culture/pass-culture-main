import React from 'react'
import PropTypes from 'prop-types'

const SubmitButton = ({ disabled }) => (
  <button
    className="header-submit"
    disabled={disabled}
    type="submit"
  >
    OK
  </button>
)

SubmitButton.defaultProps = {
  disabled: false,
}

SubmitButton.propTypes = {
  disabled: PropTypes.bool,
}

export default SubmitButton
