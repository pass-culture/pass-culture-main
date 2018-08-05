import { Icon } from 'pass-culture-shared'
import React from 'react'
import { Link } from 'react-router-dom'

import Main from '../layout/Main'

const BetaPage = () => (
  <Main name="beta" redBg>
    <h1>
      <strong>
        {'Bienvenue dans la version beta'}
      </strong>
      <span>
        {'du Pass Culture'}
      </span>
    </h1>
    <p>
      {"Et merci de votre participation pour nous aider à l'améliorer !"}
    </p>
    <footer>
      <Link
        to="/inscription"
        className="button is-secondary has-text-weight-light is-italic"
      >
        {"C'est par là"}
        <Icon svg="ico-next" alt="Suivant" />
      </Link>
    </footer>
  </Main>
)

export default BetaPage
