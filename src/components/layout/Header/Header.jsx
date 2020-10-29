import { Menu, MenuList, MenuButton, MenuItem, MenuLink } from '@reach/menu-button'
import '@reach/menu-button/styles.css'
import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { NavLink } from 'react-router-dom'
import { reinitializeData } from 'redux-saga-data'

import * as pcapi from 'repository/pcapi/pcapi'

import Icon from '../Icon'
import Logo from '../Logo'

import { HELP_PAGE_URL, STYLEGUIDE_ACTIVE } from './_constants'

class Header extends PureComponent {
  constructor() {
    super()
    this.state = {
      showMobileMenu: false,
    }
  }

  onHandleSuccessRedirect = () => '/connexion'

  handleOnClick = showMobileMenu => () => {
    this.setState({
      showMobileMenu: !showMobileMenu,
    })
  }

  onSignoutClick = () => {
    const { dispatch } = this.props
    pcapi.signout()
      .then(() => {
        dispatch(reinitializeData())
      })
      .catch(() => {
        // dispatch(reinitializeData())
      })
  }

  render() {
    const { isSmall, name, whiteHeader, offerers } = this.props
    const { showMobileMenu } = this.state

    return (
      <header
        className={classnames('navbar', {
          'is-primary': !whiteHeader,
          'is-small': isSmall,
        })}
      >
        <div className="container">
          <div className="navbar-brand">
            <Logo
              className="navbar-item"
              whiteHeader={whiteHeader}
            />
            <button
              className="navbar-burger"
              onClick={this.handleOnClick(showMobileMenu)}
              type="button"
            >
              <span />
              <span />
              <span />
            </button>
          </div>
          <div
            className={classnames('navbar-menu', {
              'is-active': showMobileMenu,
            })}
          >
            <div className="navbar-end">
              <NavLink
                className="navbar-item"
                to="/guichet"
              >
                <span className="icon">
                  <Icon svg="ico-guichet-w" />
                </span>
                <span>
                  {'Guichet'}
                </span>
              </NavLink>
              {!whiteHeader && (
                <NavLink
                  className="navbar-item"
                  to="/offres"
                >
                  <span className="icon">
                    <Icon svg="ico-offres-w" />
                  </span>
                  <span>
                    {'Offres'}
                  </span>
                </NavLink>
              )}
              {!whiteHeader && (
                <NavLink
                  className="navbar-item"
                  to="/reservations"
                >
                  <span className="icon">
                    <Icon svg="ico-bookings-w" />
                  </span>
                  <span>
                    {'Réservations'}
                  </span>
                </NavLink>
              )}
              <Menu>
                <MenuButton>
                  <span className="icon">
                    <Icon svg={`ico-user-circled${whiteHeader ? '' : '-w'}`} />
                  </span>
                  <span>
                    {name}
                  </span>
                </MenuButton>
                <MenuList>
                  <MenuLink
                    as="a"
                    href="/profil"
                  >
                    <span className="icon">
                      <Icon svg="ico-user" />
                    </span>
                    <span>
                      {'Profil'}
                    </span>
                  </MenuLink>
                  <MenuLink
                    as="a"
                    href="/structures"
                  >
                    <span className="icon">
                      <Icon svg="ico-structure-r" />
                    </span>
                    <span>
                      {offerers.length > 1 ? 'Structures juridiques' : 'Structure juridique'}
                    </span>
                  </MenuLink>
                  <MenuLink
                    as="a"
                    href="/remboursements"
                  >
                    <span className="icon">
                      <Icon svg="ico-compta" />
                    </span>
                    <span>
                      {'Remboursements'}
                    </span>
                  </MenuLink>
                  {STYLEGUIDE_ACTIVE && (
                    <MenuLink
                      as="a"
                      href="/styleguide"
                    >
                      <span className="icon">
                        <Icon svg="ico-stars" />
                      </span>
                      <span>
                        {'Styleguide'}
                      </span>
                    </MenuLink>
                  )}
                  <MenuLink
                    as="a"
                    href={HELP_PAGE_URL}
                  >
                    <span className="icon">
                      <Icon svg="ico-help" />
                    </span>
                    <span>
                      {'Aide'}
                    </span>
                  </MenuLink>
                  <MenuItem onSelect={this.onSignoutClick}>
                    <span className="icon">
                      <Icon svg="ico-deconnect" />
                    </span>
                    <span>
                      {'Déconnexion'}
                    </span>
                  </MenuItem>
                </MenuList>
              </Menu>
            </div>
          </div>
        </div>
      </header>
    )
  }
}

Header.defaultProps = {
  isSmall: false,
  whiteHeader: false,
}

Header.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isSmall: PropTypes.bool,
  name: PropTypes.string.isRequired,
  offerers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  whiteHeader: PropTypes.bool,
}

export default Header
