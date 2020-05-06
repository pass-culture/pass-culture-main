import React from 'react'
import {toast} from 'react-toastify'
import Icon from "../Icon/Icon"

export const displaySnackbar = (message, status) => {
  return (
    toast(message, {
      className: `toast-default toast-${status}`,
      closeButton: <Icon
        alt="Fermer"
        svg="ico-close-toast"
                   />
    })
  )
}
