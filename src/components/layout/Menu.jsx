import { Icon } from 'pass-culture-shared'
import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'

import SignoutButton from './SignoutButton'
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
          {menu.links.map(({ icon, path, title }, index) => (
            <div className="has-text-centered" key={index}>
              <NavLink to={path}>
                <div className="heading">
                  <Icon svg={icon} />
                </div>
                <p className="title">{title}</p>
              </NavLink>
            </div>
          ))}
          <SignoutButton />
        </nav>
      </div>
    )
  }
}

export default Menu
