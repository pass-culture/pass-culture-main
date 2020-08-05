import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

const PopinButton = ({ action, label }) => {
  const [isDisabled, setIsDisabled] = useState(false)

  const onClick = useCallback(() => {
    setIsDisabled(true)
    action()
  }, [action])

  return (
    <button
      className="popin-button"
      disabled={isDisabled}
      key={label}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  )
}

PopinButton.propTypes = {
  action: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
}

export default PopinButton
