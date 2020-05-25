import React from 'react'
import { toast } from 'react-toastify'

import Icon from '../components/layout/Icon/Icon'

export const snackbar = (message, status) =>
  toast[status](message, {
    closeButton: <Icon
      alt="Fermer"
      svg="ico-close-toast"
                 />,
    hideProgressBar: false,
    position: 'top-right',
  })
