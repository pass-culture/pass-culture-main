import React from 'react'
import { Redirect } from 'react-router'

import { ReactComponent as CounterSvg } from 'components/layout/Header/assets/counter.svg'
import { ReactComponent as OffersSvg } from 'components/layout/Header/assets/offers.svg'
import PageTitle from 'components/layout/PageTitle/PageTitle'

import Card from './Card/Card'

const Home = ({ isNewHomepageActive }) =>
  isNewHomepageActive ? (
    <Redirect to="/v2/accueil" />
  ) : (
    <div className="home-cards columns">
      <PageTitle title="Accueil" />
      <Card
        SvgElement={CounterSvg}
        navLink="/guichet"
        text="Enregistrez les codes de réservation des porteurs du Pass."
        title="Guichet"
      />
      <Card
        SvgElement={OffersSvg}
        navLink="/offres"
        text="Créez et mettez en avant vos offres présentes sur le Pass."
        title="Offres"
      />
    </div>
  )

export default Home
