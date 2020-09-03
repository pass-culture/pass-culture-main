import React from 'react'
import PropTypes from 'prop-types'
import Icon from '../Icon'

const GenericError = ({ message }) => (
  <div className="generic-error">
    <Icon svg="picto-echec" />
    <div className="generic-error-message">
      { message }
    </div>
  </div>
)

GenericError.propTypes = {
  message: PropTypes.string.isRequired
}

export default GenericError
