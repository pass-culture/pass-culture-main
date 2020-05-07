import React from 'react'
import PropTypes from 'prop-types'
import { toast } from 'react-toastify'

import Icon from '../Icon/Icon'

export const snackbar = (message, status) => (
  toast(message, {
    className: `toast-default toast-${status}`,
    closeButton: <Icon
      alt="Fermer"
      svg="ico-close-toast"
                 />
  })
)

snackbar.propTypes = {
  message: PropTypes.string.isRequired,
  status: PropTypes.string.isRequired
}
