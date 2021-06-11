import PropTypes from 'prop-types'
import React from 'react'

import { ReactComponent as SpinnerIcon } from 'components/layout/SubmitButton/assets/loader.svg'

const SubmitButton = ({ children, className, disabled, isLoading, onClick }) => {
  return (
    <button
      className={`primary-button loading-spinner submit-button ${className}`}
      disabled={disabled || isLoading}
      onClick={onClick}
      type="submit"
    >
      {isLoading ? <SpinnerIcon /> : children}
    </button>
  )
}
SubmitButton.defaultProps = {
  children: 'Enregistrer',
  className: '',
  disabled: false,
  isLoading: false,
  onClick: () => {},
}

SubmitButton.propTypes = {
  children: PropTypes.node,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  isLoading: PropTypes.bool,
  onClick: PropTypes.func,
}

export default SubmitButton
