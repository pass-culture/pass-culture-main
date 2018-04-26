import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Icon from '../layout/Icon'
// import ProfilePicture from './ProfilePicture'
import { requestData } from '../../reducers/data'
import { closeModal } from '../../reducers/modal'
import { ROOT_PATH } from '../../utils/config'

class Menu extends Component {
  onDisableClick = event => {
    alert('Pas encore disponible')
    event.preventDefault()
  }

  onSignOutClick = () => {
    const { closeModal, requestData } = this.props
    requestData('GET', 'users/signout')
    closeModal()
  }

  render() {
    const { user } = this.props
    return (
      <div className="menu">
        <div className="menu__header">
          <div className="profile-pic">
            <img
              src={`${ROOT_PATH}/icons/avatar-default-w-XL.svg`}
              alt="Avatar"
              className="avatar"
            />
            {user && user.publicName}
          </div>
          <div className="account">
            <div>Mon Pass</div>
            <div>
              <strong>——&nbsp;€</strong>
            </div>
          </div>
        </div>
        <ul>
          <li>
            <NavLink to="/decouverte">
              <div className="menu-icon">
                <Icon svg="ico-offres-w" />
              </div>
              Les offres
            </NavLink>
          </li>
          <li>
            <NavLink to="/reservations">
              <div className="menu-icon">
                <Icon svg="ico-calendar-w" />
              </div>
              Mes réservations
            </NavLink>
          </li>
          <li>
            <NavLink to="/favoris">
              <div className="menu-icon">
                <Icon svg="ico-like-w" />
              </div>
              Mes préférés
            </NavLink>
          </li>
          <li className="disabled">
            <NavLink to="/reglages" onClick={this.onDisableClick}>
              <div className="menu-icon">
                <Icon svg="ico-settings-w" />
              </div>
              Réglages
            </NavLink>
          </li>
          <li className="disabled">
            <NavLink to="/profil" onClick={this.onDisableClick}>
              <div className="menu-icon">
                <Icon svg="ico-user-w" />
              </div>
              Mon profil
            </NavLink>
          </li>
          <li>
            <NavLink to="/mentions-legales">
              <div className="menu-icon">
                <Icon svg="ico-settings-w" />
              </div>
              Mentions légales
            </NavLink>
          </li>
        </ul>
        <div className="stick-to-bottom">
          <button onClick={this.onSignOutClick} className="button">
            <div className="menu-icon">
              <Icon svg="ico-deconnect-w" />
            </div>
            Déconnexion
          </button>
        </div>
      </div>
    )
  }
}

export default connect(state => ({ user: state.user }), {
  closeModal,
  requestData,
})(Menu)
