import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon'

const GenericError = ({ message }) => (
  <div className="generic-error">
    <Icon svg="ico-notification-error-red" />
    <div className="generic-error-message">
      {message}
    </div>
  </div>
)

GenericError.propTypes = {
  message: PropTypes.string.isRequired,
}

export default GenericError
