import React from 'react'
import { toast } from 'react-toastify'

import Icon from '../components/layout/Icon/Icon'

export const snackbar = (message, status) =>
  toast(message, {
    className: `toast-default toast-${status}`,
    closeButton: <Icon
      alt="Fermer"
      svg="ico-close-toast"
                 />,
  })
