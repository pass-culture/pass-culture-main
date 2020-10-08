import React from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'

import Card from './Card/Card'

const Home = () => (
  <div className="home-cards columns">
  <PageTitle title="Accueil" />
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
)

export default Home
