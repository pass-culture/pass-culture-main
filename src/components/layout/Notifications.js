import React from 'react'
import { Slide, ToastContainer } from 'react-toastify'

// eslint-disable-next-line
const CloseButton = ({ closeToast }) => (
  <button
    type="button"
    onClick={closeToast}
    className="react-toastify-custom-close-button no-background no-border is-red-text"
  >
    <i className="icon-retina icon-ico-close" />
  </button>
)

const Notifications = ({ ...rest }) => (
  // https://github.com/fkhadra/react-toastify#toastcontainer
  <ToastContainer
    hideProgressBar
    transition={Slide}
    position="top-center"
    {...rest}
    closeButton={<CloseButton />}
    bodyClassName="react-toastify-body"
    className="react-toastify-container"
    toastClassName="react-toastify-toast"
  />
)

export default Notifications
