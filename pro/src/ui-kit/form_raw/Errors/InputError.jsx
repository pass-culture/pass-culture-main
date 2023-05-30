/* istanbul ignore file */
import PropTypes from 'prop-types'
import React from 'react'

const InputError = ({ children, name }) => {
  const inputErrorExtraProps = name
    ? {
        'data-testid': `input-error-field-${name}`,
      }
    : {}
  return (
    <span className="it-errors" {...inputErrorExtraProps}>
      <pre>{children}</pre>
    </span>
  )
}

InputError.defaultProps = {
  name: '',
}

InputError.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]).isRequired,
  name: PropTypes.string,
}

export default InputError
