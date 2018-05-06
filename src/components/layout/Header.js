import React, { Component } from 'react'
import { connect } from 'react-redux'

import Menu from './Menu'
import { showModal } from '../../reducers/modal'

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
            <a className="navbar-item is-active">
              Home
            </a>
            <a className="navbar-item">
              Examples
            </a>
            <a className="navbar-item">
              Documentation
            </a>
            <span className="navbar-item">
              <a className="button is-success is-inverted">
                <span className="icon">
                  <i className="fab fa-github"></i>
                </span>
                <span>Download</span>
              </a>
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default connect(null, { showModal })(Header)
