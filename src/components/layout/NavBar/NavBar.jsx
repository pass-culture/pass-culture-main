import PropTypes from 'prop-types'
import React from 'react'

import { Link } from 'react-router-dom'

const isPresent = path =>
  RegExp(
    '(/reservation|/informations|/mot-de-passe|/mentions-legales|/activation/|/criteres-(.*)|/tri|/filtres(.*)|/bienvenue|/typeform|/beta|/connexion|/mot-de-passe-perdu|/activation/(.*)|/inscription)$'
  ).test(path)

const NavBar = ({ path }) =>
  !isPresent(path) ? (
    <nav className="navbar">
      <ul>
        <li>
          <Link to="/decouverte">
            {'Découverte'}
          </Link>
        </li>
        <li>
          <Link to="/recherche">
            {'Recherche'}
          </Link>
        </li>
        <li>
          <Link to="/reservations">
            {'Reservations'}
          </Link>
        </li>
        <li>
          <Link to="/favoris">
            {'Favoris'}
          </Link>
        </li>
        <li>
          <Link to="/profil">
            {'Profil'}
          </Link>
        </li>
      </ul>
    </nav>
  ) : null

NavBar.propTypes = {
  path: PropTypes.string.isRequired,
}

export default NavBar
