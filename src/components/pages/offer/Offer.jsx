import PropTypes from 'prop-types'
import React from 'react'

import DetailsContainer from '../../layout/Details/DetailsContainer'
import HeaderContainer from '../../layout/Header/HeaderContainer'

const Offer = ({ getOfferById }) => (
  <main className="page teaser-list">
    <HeaderContainer title="Offre" />
    <DetailsContainer getOfferById={getOfferById} />
  </main>
)

Offer.propTypes = {
  getOfferById: PropTypes.func.isRequired,
}

export default Offer
