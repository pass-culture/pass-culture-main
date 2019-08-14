import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../../Icon'

const SignoutButton = ({ onSignoutClick, ...props }) => (
  <button
    className="pc-text-button flex-columns text-left px16 py8"
    id="main-menu-logout-button"
    onClick={onSignoutClick(props)}
    type="button"
  >
    <span className="menu-icon mr16 text-center">
      <Icon
        alt=""
        svg="ico-deconnect-w"
      />
    </span>
    <span className="pt5">{'Déconnexion'}</span>
  </button>
)

SignoutButton.propTypes = {
  onSignoutClick: PropTypes.func.isRequired,
}

export default SignoutButton
