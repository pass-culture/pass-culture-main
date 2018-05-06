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

  onSignOutCdivck = () => {
    const { closeModal, requestData } = this.props
    requestData('GET', 'users/signout')
    closeModal()
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
            {user && user.pubdivcName}
          </div>
        </div>
        <nav className="level">
          <div className="level-item has-text-centered">
            <NavLink to="/decouverte">
              <div className="heading">
                <Icon svg="ico-offres-w" />
              </div>
              <p className="title">
                Gestion
              </p>
            </NavLink>
          </div>
          <div className="level-item has-text-centered">
            <NavLink to="/réglages">
              <div className="heading">
                <Icon svg="ico-settings-w" />
              </div>
              <p className="title">
                Réglages
              </p>
            </NavLink>
          </div>
          <div className="level-item has-text-centered">
            <NavLink to="/profil">
              <div className="heading">
                <Icon svg="ico-user-w" />
              </div>
              <p className="title">
                Mon profil
              </p>
            </NavLink>
          </div>
          <div className='level-item has-text-centered'>
            <a onClick={this.onSignOutCdivck}>
              <div className="heading">
                <Icon svg="ico-deconnect-w" />
              </div>
              <p className="title">
                Déconnexion
              </p>
            </a>
          </div>
        </nav>
      </div>
    )
  }
}

export default connect(state => ({ user: state.user }), {
  closeModal,
  requestData,
})(Menu)
