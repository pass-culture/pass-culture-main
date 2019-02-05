import React from 'react'
import { Slide, ToastContainer } from 'react-toastify'

import NotificationCloseButton from './NotificationCloseButton'

const Notifications = ({ ...rest }) => (
  // https://github.com/fkhadra/react-toastify#toastcontainer
  <ToastContainer
    hideProgressBar
    transition={Slide}
    position="top-center"
    {...rest}
    closeButton={<NotificationCloseButton />}
    bodyClassName="react-toastify-body"
    className="react-toastify-container"
    toastClassName="react-toastify-toast"
  />
)

export default Notifications
