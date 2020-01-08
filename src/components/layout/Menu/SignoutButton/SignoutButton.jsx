import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../../Icon/Icon'

const SignoutButton = ({ onSignOutClick, ...props }) => (
  <button
    className="pc-text-button flex-columns text-left px16 py8 fs16"
    id="main-menu-logout-button"
    onClick={onSignOutClick(props)}
    type="button"
  >
    <span className="menu-icon mr16 text-center">
      <Icon
        alt=""
        svg="ico-deconnect"
      />
    </span>
    <span className="pt5">
      {'Déconnexion'}
    </span>
  </button>
)

SignoutButton.propTypes = {
  onSignOutClick: PropTypes.func.isRequired,
}

export default SignoutButton
