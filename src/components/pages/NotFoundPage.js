import { Icon } from 'pass-culture-shared'
import React from 'react'
import { Link } from 'react-router-dom'

import Main from '../layout/Main'

const NotFoundPage = () => {
  return (
    <Main name="not-found" fullscreen redBg>
      <h1>
        <strong>Page Non Trouvée</strong>
      </h1>
      <p>Cette page n'a pas pu être affichée.</p>
      <footer>
        <Link
          to="/accueil"
          className="button is-secondary is-inversed has-text-weight-light is-italic">
          Revenir à l'accueil
          <Icon svg="ico-next" />
        </Link>
      </footer>
    </Main>
  )
}

export default NotFoundPage
