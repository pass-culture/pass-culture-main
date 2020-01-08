import React from 'react'
import PropTypes from 'prop-types'

import Icon from '../../layout/Icon/Icon'
import { noopnoop } from '../../../utils/functionnals'

const NotificationCloseButton = ({ closeToast }) => (
  <button
    className="react-toastify-custom-close-button no-background is-red-text"
    onClick={closeToast}
    type="button"
  >
    <Icon
      alt="Fermer la modale"
      svg="ico-close-black"
    />
  </button>
)

NotificationCloseButton.defaultProps = {
  closeToast: noopnoop,
}

NotificationCloseButton.propTypes = {
  closeToast: PropTypes.func,
}

export default NotificationCloseButton
