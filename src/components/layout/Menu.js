import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Icon from './Icon'
import SigninOut from './SigninOut'
import { ROOT_PATH } from '../../utils/config'
import menu from '../../utils/menu'

class Menu extends Component {
  onDisableClick = event => {
    alert('Pas encore disponible')
    event.preventDefault()
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
        </div>
        <nav>
          {
            menu.links.map(({ icon, path, title }, index) =>
              <div className="has-text-centered"
                key={index}>
                <NavLink to={path}>
                  <div className="heading">
                    <Icon svg={icon} />
                  </div>
                  <p className="title">
                    {title}
                  </p>
                </NavLink>
              </div>
            )
          }
          <SigninOut>
            <div className="heading">
              <Icon svg='ico-deconnect-w' />
            </div>
            <p className="title">
              Déconnexion
            </p>
          </SigninOut>
        </nav>
      </div>
    )
  }
}

export default Menu
