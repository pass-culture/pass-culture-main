import React from 'react'
import PropTypes from 'prop-types'

import { noopnoop } from '../../../utils/functionnals'

const NotificationCloseButton = ({ closeToast }) => (
  <button
    className="react-toastify-custom-close-button no-background is-red-text"
    onClick={closeToast}
    type="button"
  >
    <i className="icon-retina icon-ico-close" />
  </button>
)

NotificationCloseButton.defaultProps = {
  closeToast: noopnoop,
}

NotificationCloseButton.propTypes = {
  closeToast: PropTypes.func,
}

export default NotificationCloseButton
