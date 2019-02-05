import React from 'react'
import PropTypes from 'prop-types'

import { noopnoop } from '../../../utils/functionnals'

const NotificationCloseButton = ({ closeToast }) => (
  <button
    type="button"
    onClick={closeToast}
    className="react-toastify-custom-close-button no-background no-border is-red-text"
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
