import { Menu, MenuButton, MenuItem, MenuLink, MenuList } from '@reach/menu-button'
import '@reach/menu-button/styles.css'
import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { NavLink } from 'react-router-dom'
import { reinitializeData } from 'redux-saga-data'

import { signout } from 'repository/pcapi/pcapi'

import Icon from '../Icon'
import Logo from '../Logo'

// FIXME (Adrien S, 11/12/2020): Inject StyleGuide as a props, to avoid mocks and increase testability
import { HELP_PAGE_URL, STYLEGUIDE_ACTIVE } from './_constants'

class Header extends PureComponent {
  onHandleSuccessRedirect = () => '/connexion'

  onSignoutClick = () => {
    const { dispatch } = this.props
    signout().then(() => {
      dispatch(reinitializeData())
    })
  }

  render() {
    const { isSmall, name, offerers } = this.props

    return (
      <header
        className={classnames(
          {
            'is-small': isSmall,
          },
          'menu'
        )}
      >
        <nav>
          <div className="nav-brand">
            <Logo className="nav-item" />
          </div>
          <div className="nav-menu">
            <NavLink
              className="nav-item"
              role="menuitem"
              to="/guichet"
            >
              <span className="icon">
                <Icon svg="ico-guichet-w" />
              </span>
              <span>
                {'Guichet'}
              </span>
            </NavLink>
            <NavLink
              className="nav-item"
              role="menuitem"
              to="/offres"
            >
              <span className="icon">
                <Icon svg="ico-offres-w" />
              </span>
              <span>
                {'Offres'}
              </span>
            </NavLink>
            <NavLink
              className="nav-item"
              role="menuitem"
              to="/reservations"
            >
              <span className="icon">
                <Icon svg="ico-bookings-w" />
              </span>
              <span>
                {'Réservations'}
              </span>
            </NavLink>
            <Menu>
              <MenuButton className="nav-item">
                <span className="icon">
                  <Icon svg="ico-user-circled-w" />
                </span>
                <span>
                  {name}
                </span>
                <Icon svg="ico-arrow-down-r" />
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
                  target="_blank"
                >
                  <span className="icon">
                    <Icon svg="ico-help" />
                  </span>
                  {'Aide'}
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
        </nav>
      </header>
    )
  }
}

Header.defaultProps = {
  isSmall: false,
}

Header.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isSmall: PropTypes.bool,
  name: PropTypes.string.isRequired,
  offerers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default Header
