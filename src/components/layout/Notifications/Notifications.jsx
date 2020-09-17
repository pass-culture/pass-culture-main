import React from 'react'
import { Slide, ToastContainer } from 'react-toastify'

import Icon from '../Icon/Icon'

const Notifications = () => (
  <ToastContainer
    closeButton={(
      <Icon
        alt="Fermer"
        svg="ico-close-toast"
      />
    )}
    hideProgressBar={false}
    position="top-center"
    transition={Slide}
  />
)

export default Notifications
