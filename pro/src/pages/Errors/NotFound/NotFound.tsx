import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'ui-kit/Icon/Icon'

interface Props {
  redirect?: string
}

const NotFound = ({ redirect = '/accueil' }: Props) => (
  <main className="page fullscreen no-match" id="content">
    <Icon svg="ico-404" />
    <h1>Oh non !</h1>
    <p>Cette page n’existe pas.</p>
    <Link className="nm-redirection-link" to={redirect}>
      Retour à la page d’accueil
    </Link>
  </main>
)

export default NotFound
