import Icon from 'components/layout/Icon'
import { Link } from 'react-router-dom'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import PropTypes from 'prop-types'
import React from 'react'

const NotFound = ({ redirect }) => (
  <main className="page fullscreen no-match">
    <PageTitle title="Page inaccessible" />
    <Icon svg="ico-404" />
    <h1>Oh non !</h1>
    <p>Cette page n’existe pas.</p>
    <Link className="nm-redirection-link" to={redirect}>
      Retour à la page d’accueil
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
