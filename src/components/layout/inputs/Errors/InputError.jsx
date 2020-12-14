import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../../Icon'

const InputError = ({ name, message }) => {
  const inputErrorExtraProps = name
    ? {
        'data-testid': `input-error-field-${name}`,
      }
    : {}
  return (
    <span
      className="it-errors"
      {...inputErrorExtraProps}
    >
      <Icon
        alt="Une erreur est survenue"
        svg="ico-notification-error-red"
      />
      <pre>
        {message}
      </pre>
    </span>
  )
}

InputError.defaultProps = {
  name: '',
}

InputError.propTypes = {
  message: PropTypes.string.isRequired,
  name: PropTypes.string,
}

export default InputError
