import PropTypes from 'prop-types'
import React from 'react'

import DetailsContainer from '../../layout/Details/DetailsContainer'
import HeaderContainer from '../../layout/Header/HeaderContainer'

const Offer = ({ getOfferById }) => (
  <main className="page teaser-list">
    <HeaderContainer
      closeTitle="Retourner à la page découverte"
      closeTo="/decouverte"
      title="Offre"
    />
    <DetailsContainer getOfferById={getOfferById} />
  </main>
)

Offer.propTypes = {
  getOfferById: PropTypes.func.isRequired,
}

export default Offer
