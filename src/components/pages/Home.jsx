import { Icon } from 'pass-culture-shared'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { withRedirectToSigninWhenNotAuthenticated } from '../hocs'
import Main from '../layout/Main'

const Card = ({ svg, title, text, navLink }) => {
  return (
    <NavLink to={navLink} className="home-card column">
      <Icon svg={svg} />
      <div className="home-card-text">
        <h1 className="title is-1 is-spaced">{title}</h1>
        <p className="subtitle is-2">{text}</p>
      </div>
    </NavLink>
  )
}

const HomePage = ({ user }) => {
  return (
    <Main name="home" whiteHeader>
      <div className="home-cards columns">
        <Card
          svg="ico-guichet-w"
          title="Guichet"
          text="Enregistrez les codes de réservation des porteurs du Pass."
          navLink="/guichet"
        />
        <Card
          svg="ico-offres-w"
          title="Vos offres"
          text="Créez et mettez en avant vos offres présentes sur le Pass."
          navLink="/offres"
        />
      </div>
    </Main>
  )
}

export default withRedirectToSigninWhenNotAuthenticated(HomePage)
