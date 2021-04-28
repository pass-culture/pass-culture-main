import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'

const NotFound = ({ redirect }) => (
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

NotFound.defaultProps = {
  redirect: '/accueil',
}

NotFound.propTypes = {
  redirect: PropTypes.string,
}

export default NotFound
