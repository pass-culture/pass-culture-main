import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import classnames from 'classnames'
import get from 'lodash.get'

import Icon from './Icon'
import SignoutButton from './SignoutButton'
import Logo from './Logo'

class Header extends Component {
  constructor() {
    super()
    this.state = {
      showMobileMenu: false,
    }
  }

  render() {
    const { whiteHeader } = this.props
    return (
      <header className={classnames('navbar is primary', { 'white-header': whiteHeader })}>
        <div className="container">
          <div className="navbar-brand">
            <Logo className="navbar-item" whiteHeader />
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
          {!whiteHeader && [
            <NavLink className="navbar-item" to={'/guichet'}>
            <span className='icon'><Icon svg={'ico-guichet-w'} /></span>
            <span>Guichet</span>
          </NavLink>,

          <NavLink className="navbar-item" to={'/offres'}>
          <span className='icon'><Icon svg={'ico-offres-w'} /></span>
          <span>Vos offres</span>
        </NavLink>
      ]}
      <div className="navbar-item has-dropdown is-hoverable">
        <a className="navbar-link" href="#">
          <span className='icon'>
            {!whiteHeader ?
              <Icon svg='ico-user-circled-w' />
              : <Icon svg='ico-user-circled' />
            }
          </span>
          <span className={classnames('white-header': whiteHeader)}>
            {this.props.name}
          </span>
        </a>
        <div className="navbar-dropdown is-right">
          <NavLink to={'/profil'} className='navbar-item'>
          <span className='icon'><Icon svg={'ico-user'} /></span>
          <span>Profil</span>
        </NavLink>
        <NavLink to={'/structures'} className='navbar-item'>
        <span className='icon'><Icon svg={'ico-structure'} /></span>
        <span>Structures</span>
      </NavLink>
      <NavLink to={'/delegations'} className='navbar-item'>
      <span className='icon'><Icon svg={'ico-delegation'} /></span>
      <span>Délégations</span>
    </NavLink>
    <NavLink to={'/comptabilite'} className='navbar-item'>
    <span className='icon'><Icon svg={'ico-compta'} /></span>
    <span>Comptabilité</span>
  </NavLink>
  <SignoutButton tagName='a' className='navbar-item'>
    <span className='icon'><Icon svg={'ico-deconnect'} /></span>
    <span>Déconnexion</span>
  </SignoutButton>
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
