import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Menu from './Menu'
import SigninOut from './SigninOut'
import { showModal } from '../../reducers/modal'
import menu from '../../utils/menu'

const Header = ({ showModal }) => {
  return (
    <header className="navbar">
      <div className="container">
        <div className="navbar-brand">
          <a className="navbar-item">
            <img src="https://bulma.io/images/bulma-type-white.png" alt="Logo" />
          </a>
          <span className="navbar-burger burger"
            data-target="navbarMenuHeroC"
            onClick={() => showModal(<Menu />, { fromDirection: 'top' })}>
            <span></span>
            <span></span>
            <span></span>
          </span>
        </div>
        <div id="navbarMenuHeroC" className="navbar-menu">
          <div className="navbar-end">
            {
              menu.links.map(({ path, title }, index) => (
                <NavLink className="navbar-item is-active"
                  key={index}
                  to={path}
                >
                  {title}
                </NavLink>
              ))
            }
          </div>
        </div>
        <SigninOut className='navbar-item is-active is-hidden-mobile'>
          <a className="navbar-item is-active">
            Déconnexion
          </a>
        </SigninOut>
      </div>
    </header>
  )
}

export default connect(null, { showModal })(Header)
