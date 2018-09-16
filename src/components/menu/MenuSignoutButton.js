/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { Icon, requestData } from 'pass-culture-shared'

const MenuSignoutButton = ({ onSignOutClick }) => (
  <button
    type="button"
    id="main-menu-logout-button"
    className="pc-text-button flex-columns text-left p16"
    onClick={onSignOutClick}
  >
    <span className="menu-icon mr16 text-center">
      <Icon svg="ico-deconnect-w" alt="" />
    </span>
    <span>Déconnexion</span>
  </button>
)

MenuSignoutButton.propTypes = {
  onSignOutClick: PropTypes.func.isRequired,
}

const mapDispatchToProps = (dispatch, { history }) => ({
  onSignOutClick: () => {
    requestData('GET', 'users/signout', {
      handleSuccess: () => {
        history.push('/connexion')
        this.toggleMainMenu()
      },
    })
  },
})

export default compose(
  withRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(MenuSignoutButton)
