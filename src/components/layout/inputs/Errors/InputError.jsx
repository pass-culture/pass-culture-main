import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../../Icon'

const InputError = ({ message }) => (
  <span className="it-errors">
    <Icon
      alt="Une erreur est survenue"
      svg="picto-echec"
    />
    <pre>
      {message}
    </pre>
  </span>
)

InputError.propTypes = {
  message: PropTypes.string.isRequired,
}

export default InputError
