import React from 'react'
import { NavLink } from 'react-router-dom'

import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs'
import Icon from '../../layout/Icon'
import Main from '../../layout/Main'

const Card = ({ svg, title, text, navLink }) => {
  return (
    <NavLink
      className="home-card column"
      to={navLink}
    >
      <Icon svg={svg} />
      <div className="home-card-text">
        <h1 className="title is-1 is-spaced">{title}</h1>
        <p className="subtitle is-2">{text}</p>
      </div>
    </NavLink>
  )
}

const Home = ({ currentUser }) => {
  return (
    <Main
      name="home"
      whiteHeader
    >
      <div className="home-cards columns">
        <Card
          navLink="/guichet"
          svg="ico-guichet-w"
          text="Enregistrez les codes de réservation des porteurs du Pass."
          title="Guichet"
        />
        <Card
          navLink="/offres"
          svg="ico-offres-w"
          text="Créez et mettez en avant vos offres présentes sur le Pass."
          title="Vos offres"
        />
      </div>
    </Main>
  )
}

export default withRedirectToSigninWhenNotAuthenticated(Home)
