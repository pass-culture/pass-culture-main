import React from 'react'
import { Slide, ToastContainer } from 'react-toastify'

import NotificationCloseButton from './NotificationCloseButton'

const Notifications = ({ ...rest }) => (
  // https://github.com/fkhadra/react-toastify#toastcontainer
  <ToastContainer
    hideProgressBar
    position="top-center"
    transition={Slide}
    {...rest}
    bodyClassName="react-toastify-body"
    className="react-toastify-container"
    closeButton={<NotificationCloseButton />}
    toastClassName="react-toastify-toast"
  />
)

export default Notifications
