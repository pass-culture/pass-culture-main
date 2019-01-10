/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { Icon } from 'pass-culture-shared'

import { mapDispatchToProps, mapStateToProps } from './connect'

const MenuSignoutButton = ({ onSignoutClick, ...ownProps }) => (
  <button
    type="button"
    id="main-menu-logout-button"
    className="pc-text-button flex-columns text-left p16"
    onClick={onSignoutClick(ownProps)}
  >
    <span className="menu-icon mr16 text-center">
      <Icon svg="ico-deconnect-w" alt="" />
    </span>
    <span>Déconnexion</span>
  </button>
)

MenuSignoutButton.propTypes = {
  onSignoutClick: PropTypes.func.isRequired
}

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(MenuSignoutButton)
