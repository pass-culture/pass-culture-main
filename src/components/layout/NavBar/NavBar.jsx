import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

const NavBar = ({ isFeatureEnabled, routes }) => (
  <nav className="navbar">
    <ul>
      {routes.map(route => {
        if (route.to && isFeatureEnabled(route.featureName)) {
          return (
            <li key={route.to}>
              <NavLink to={route.to}>
                <route.icon />
              </NavLink>
            </li>
          )
        }
      })}
    </ul>
  </nav>
)

NavBar.propTypes = {
  isFeatureEnabled: PropTypes.func.isRequired,
  routes: PropTypes.arrayOf(PropTypes.shape().isRequired).isRequired,
}

export default NavBar
