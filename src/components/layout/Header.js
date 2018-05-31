import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import classnames from 'classnames'
import get from 'lodash.get'

import Icon from './Icon'
import SignoutButton from './SignoutButton'
import Logo from './Logo'
import menu from '../../utils/menu'

class Header extends Component {
  constructor() {
    super()
    this.state = {
      showMobileMenu: false,
    }
  }

  render() {
    return (
      <header className="navbar is-primary">
        <div className="container">
          <div className="navbar-brand">
            <Logo className="navbar-item" />
            <span className="navbar-burger" onClick={e => this.setState({
              showMobileMenu: !this.state.showMobileMenu
            })}>
              <span></span>
              <span></span>
              <span></span>
            </span>
          </div>
          <div className={classnames("navbar-menu", {
            'is-active': this.state.showMobileMenu
          })}>
            <div className="navbar-end">
              {
                menu.links.map(({ path, title, icon }, index) => (
                  <NavLink className="navbar-item"
                    key={index}
                    to={path}
                  >
                    <span className='icon'><Icon svg={icon} /></span>
                    <span>{` ${title}`}</span>
                  </NavLink>
                ))
              }
              <div className="navbar-item has-dropdown is-hoverable">
                <a className="navbar-link" href="/profil">
                  <span className='icon'>
                    <Icon svg='ico-user-w' />
                  </span>
                  <span>
                    {this.props.name}
                  </span>
                </a>
                <div className="navbar-dropdown is-right">
                  <SignoutButton tagName='a' className='navbar-item'>Déconnexion</SignoutButton>
                </div>
              </div>
            </div>
          </div>

        </div>
      </header>
    )
  }
}

export default connect(state => ({
  name: get(state, 'user.publicName')
}), {})(Header)
