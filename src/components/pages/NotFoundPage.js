import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../layout/Icon'
import PageWrapper from '../layout/PageWrapper'

const NotFoundPage = () => {
  return (
    <PageWrapper name="not-found" fullscreen redBg>
      <h1>
        <strong>Page Non Trouvée</strong>
      </h1>
      <p>Cette page n'a pas pu être affichée.</p>
      <footer>
        <Link
          to="/"
          className="button is-secondary is-inversed has-text-weight-light is-italic"
        >
          Revenir à l'accueil
          <Icon svg="ico-next" />
        </Link>
      </footer>
    </PageWrapper>
  )
}

export default NotFoundPage
