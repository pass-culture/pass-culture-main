import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'

const NoMatch = ({ redirect }) => (
  <main className="page fullscreen no-match">
    <Icon svg="ico-404" />
    <div className="nm-title">
      {'Oh non !'}
    </div>
    <div className="nm-subtitle">
      {"Cette page n'existe pas."}
    </div>
    <Link
      className="nm-redirection-link"
      to={redirect}
    >
      {"Retour à la page d'accueil"}
    </Link>
  </main>
)

NoMatch.defaultProps = {
  redirect: '/accueil',
}

NoMatch.propTypes = {
  redirect: PropTypes.string,
}

export default NoMatch
