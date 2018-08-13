import PropTypes from 'prop-types'
import { closeModal, Icon, requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter, NavLink } from 'react-router-dom'
import { compose } from 'redux'

import { ROOT_PATH } from '../utils/config'

class Menu extends Component {
  onDisableClick = event => {
    alert('Pas encore disponible')
    event.preventDefault()
  }

  onSignOutClick = () => {
    const { dispatchCloseModal, history, dispatchRequestData } = this.props
    dispatchRequestData('GET', 'users/signout', {
      handleSuccess: () => {
        history.push('/connexion')
        dispatchCloseModal()
      },
    })
  }

  render() {
    const { user } = this.props
    return (
      <div className="menu">
        <div className="header">
          <div className="profile-pic">
            <img
              src={`${ROOT_PATH}/icons/avatar-default-w-XL.svg`}
              alt="Avatar"
              className="avatar"
            />
            {user && user.publicName}
          </div>
          <div className="account">
            <div>
Mon Pass
            </div>
            <div>
              <strong>
——&nbsp;€
              </strong>
            </div>
          </div>
        </div>
        <ul>
          <li>
            <NavLink to="/decouverte">
              <div className="menu-icon">
                <Icon svg="ico-offres-w" alt="Les offres" />
              </div>
              Les offres
            </NavLink>
          </li>
          <li>
            <NavLink to="/reservations">
              <div className="menu-icon">
                <Icon svg="ico-calendar-w" alt="Mes réservations" />
              </div>
              Mes réservations
            </NavLink>
          </li>
          <li>
            <NavLink to="/favoris">
              <div className="menu-icon">
                <Icon svg="ico-like-w" alt="Mes préférés" />
              </div>
              Mes préférés
            </NavLink>
          </li>
          <li>
            <NavLink to="/reglages" onClick={this.onDisableClick} disabled>
              <div className="menu-icon">
                <Icon svg="ico-settings-w" alt="Réglages" />
              </div>
              Réglages
            </NavLink>
          </li>
          <li>
            <NavLink to="/profil" onClick={this.onDisableClick} disabled>
              <div className="menu-icon">
                <Icon svg="ico-user-w" alt="Mon profil" />
              </div>
              Mon profil
            </NavLink>
          </li>
          <li>
            <NavLink to="/mentions-legales">
              <div className="menu-icon">
                <Icon svg="ico-txt-w" alt="Mentions légales" />
              </div>
              Mentions légales
            </NavLink>
          </li>
          <li>
            <a href="mailto:pass@culture.gouv.fr">
              <div className="menu-icon">
                <Icon svg="ico-mail-w" alt="Nous contacter" />
              </div>
              Nous contacter
            </a>
          </li>
          <li>
            <button
              type="button"
              onClick={this.onSignOutClick}
              className="button-as-link"
            >
              <div className="menu-icon">
                <Icon svg="ico-deconnect-w" alt="Déconnexion" />
              </div>
              Déconnexion
            </button>
          </li>
        </ul>
      </div>
    )
  }
}

Menu.propTypes = {
  dispatchCloseModal: PropTypes.func.isRequired,
  dispatchRequestData: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  user: PropTypes.object.isRequired,
}

export default compose(
  withRouter,
  connect(
    state => ({ user: state.user }),
    {
      dispatchCloseModal: closeModal,
      dispatchRequestData: requestData,
    }
  )
)(Menu)
