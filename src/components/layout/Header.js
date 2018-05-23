import React from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Menu from './Menu'
import { showModal } from '../../reducers/modal'
import { ROOT_PATH } from '../../utils/config'
import menu from '../../utils/menu'

const Header = ({ showModal }) => {
  return (
    <header className="header navbar red-bg">
      <div className="container">
        <div className="navbar-brand">
          <NavLink to='/' className="navbar-item is-italic">
            <img src={`${ROOT_PATH}/icon/app-icon-app-store.png`} alt="Logo" />
            <b> Pass </b> Culture PRO
          </NavLink>
          <span className="navbar-burger burger"
            data-target="navbarMenuHeroC"
            onClick={() => showModal(<Menu />,
              {
                fromDirection: 'right',
                isClosingOnLocationChange: true
              })}>
            <span></span>
            <span></span>
            <span></span>
          </span>
        </div>
        <div id="navbarMenuHeroC" className="navbar-menu">
          <div className="navbar-end">
            {
              menu.links.map(({ path, title }, index) => (
                <NavLink className="navbar-item is-active is-outlined"
                  key={index}
                  to={path}
                >
                  {title}
                </NavLink>
              ))
            }
          </div>
        </div>

      </div>
    </header>
  )
}

export default connect(null, { showModal })(Header)
