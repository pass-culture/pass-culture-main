import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { isPathWithNavBar } from './domain/isPathWithNavBar'
import { IcoNavBookings } from './Icons/IcoNavBookings'
import { IcoNavDiscovery } from './Icons/IcoNavDiscovery'
import { IcoNavFavorites } from './Icons/IcoNavFavorites'
import { IcoNavProfile } from './Icons/IcoNavProfile'
import { IcoNavSearch } from './Icons/IcoNavSearch'

const NavBar = ({ path }) =>
  isPathWithNavBar(path) ? (
    <nav className="navbar">
      <ul>
        <li>
          <NavLink to="/decouverte">
            <IcoNavDiscovery />
          </NavLink>
        </li>
        <li>
          <NavLink to="/recherche">
            <IcoNavSearch />
          </NavLink>
        </li>
        <li>
          <NavLink to="/reservations">
            <IcoNavBookings />
          </NavLink>
        </li>
        <li>
          <NavLink to="/favoris">
            <IcoNavFavorites />
          </NavLink>
        </li>
        <li>
          <NavLink to="/profil">
            <IcoNavProfile />
          </NavLink>
        </li>
      </ul>
    </nav>
  ) : null

NavBar.propTypes = {
  path: PropTypes.string.isRequired,
}

export default NavBar
