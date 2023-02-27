import React from 'react'
import { Link } from 'react-router-dom'

import PageTitle from 'components/PageTitle/PageTitle'
import Icon from 'ui-kit/Icon/Icon'

interface Props {
  redirect?: string
}

const NotFound = ({ redirect = '/accueil' }: Props) => (
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

export default NotFound
