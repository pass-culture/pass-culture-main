import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { isPathWithNavBar } from './domain/isPathWithNavBar'

const NavBar = ({ isFeatureEnabled, path, routes }) =>
  isPathWithNavBar(path) ? (
    <nav className="navbar">
      <ul>
        {routes.map(route => {
          if (route.to && isFeatureEnabled(route.featureName)) {
            if (path.startsWith(route.to)) {
              return (
                <li key={route.to}>
                  <span className="active">
                    <route.icon />
                  </span>
                </li>
              )
            } else {
              return (
                <li key={route.to}>
                  <NavLink to={route.to}>
                    <route.icon />
                  </NavLink>
                </li>
              )
            }
          }
        })}
      </ul>
    </nav>
  ) : null

NavBar.propTypes = {
  isFeatureEnabled: PropTypes.func.isRequired,
  path: PropTypes.string.isRequired,
  routes: PropTypes.arrayOf(PropTypes.shape().isRequired).isRequired,
}

export default NavBar
