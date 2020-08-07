import PropTypes from 'prop-types'
import React from 'react'
import { Route } from 'react-router'

import DetailsContainer from '../../layout/Details/DetailsContainer'
import CloseLink from '../../layout/Header/CloseLink/CloseLink'

const Offer = ({ homepageIsDisabled, match }) => (
  <Route
    exact
    path={`${match.path}/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
    sensitive
  >
    <main className="offer-page">
      <CloseLink
        closeTitle="Fermer"
        closeTo={`${homepageIsDisabled ? '/decouverte' : '/accueil'}`}
      />
      <DetailsContainer />
    </main>
  </Route>
)

Offer.defaultProps = {
  homepageIsDisabled: true
}

Offer.propTypes = {
  homepageIsDisabled: PropTypes.bool,
  match: PropTypes.shape({
    path: PropTypes.string.isRequired,
  }).isRequired,
}

export default Offer
