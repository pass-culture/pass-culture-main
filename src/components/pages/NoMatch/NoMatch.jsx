import React from 'react'
import { NavLink } from 'react-router-dom'
import { ROOT_PATH } from '../../../utils/config'
import PropTypes from 'prop-types'

const NoMatch = ({ redirect }) => {
  return (
    <div className="page fullscreen no-match">
      <img
        alt=""
        src={`${ROOT_PATH}/icons/ico-404.svg`}
      />
      <h1>
        {'Oh non !'}
      </h1>
      <p className="subtitle">
        {"Cette page n'existe pas."}
      </p>
      <div className="redirection-link">
        <NavLink to={redirect}>
          {"Retour à la page d'accueil"}
        </NavLink>
      </div>
    </div>
  )
}

NoMatch.defaultProps = {
  redirect: '/offres',
}

NoMatch.propTypes = {
  redirect: PropTypes.string,
}

export default NoMatch
