import PropTypes from 'prop-types'
import React from 'react'

import DetailsContainer from '../../layout/Details/DetailsContainer'
import CloseLink from '../../layout/Header/CloseLink/CloseLink'

const buildCloseToUrl = () => {
  return '/decouverte'
}

const Offer = ({ getOfferById }) => (
  <main className="offer-page">
    <CloseLink
      closeTitle="Fermer"
      closeTo={buildCloseToUrl()}
    />
    <DetailsContainer getOfferById={getOfferById} />
  </main>
)

Offer.propTypes = {
  getOfferById: PropTypes.func.isRequired,
}

export default Offer
