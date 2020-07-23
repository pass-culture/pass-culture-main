import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import { Route } from 'react-router'

import MyFavoriteDetailsContainer from './MyFavoriteDetails/MyFavoriteDetailsContainer'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import MyFavoritesList from './MyFavoritesList/MyFavoritesListContainer'

const MyFavorites = ({ match }) => (
  <Fragment>
    <MyFavoritesList />

    <Route
      exact
      path={`${match.path}/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId(vide|[A-Z0-9]+)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
      sensitive
    >
      <div className="offer-details">
        <HeaderContainer
          shouldBackFromDetails
          title="Favoris"
        />
        <MyFavoriteDetailsContainer
          bookingPath={`${match.path}/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId(vide|[A-Z0-9]+)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
        />
      </div>
    </Route>
  </Fragment>
)

MyFavorites.propTypes = {
  match: PropTypes.shape({
    path: PropTypes.string.isRequired,
  }).isRequired,
}

export default MyFavorites
