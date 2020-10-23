import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../../Icon'

const TextInputError = ({ message }) => (
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

TextInputError.propTypes = {
  message: PropTypes.string.isRequired,
}

export default TextInputError
