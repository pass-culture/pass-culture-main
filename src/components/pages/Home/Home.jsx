import React from 'react'

import Main from 'components/layout/Main'
import PageTitle from 'components/layout/PageTitle/PageTitle'

import Card from './Card/Card'

const Home = () => (
  <Main
    name="home"
    whiteHeader
  >
    <PageTitle title="Accueil" />
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
        title="Offres"
      />
    </div>
  </Main>
)

export default Home
