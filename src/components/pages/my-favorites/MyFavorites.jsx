import React from 'react'
import { Route, Switch } from 'react-router'

import MyFavoriteDetailsContainer from './MyFavoriteDetails/MyFavoriteDetailsContainer'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import MyFavoritesList from './MyFavoritesList/MyFavoritesListContainer'

const MyFavorites = () => (
  <Switch>
    <Route
      exact
      path="/favoris"
    >
      <MyFavoritesList />
    </Route>
    <Route
      exact
      path="/favoris/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId(vide|[A-Z0-9]+)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?"
      sensitive
    >
      <HeaderContainer
        shouldBackFromDetails
        title="Favoris"
      />
      <MyFavoriteDetailsContainer bookingPath="/favoris/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId(vide|[A-Z0-9]+)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?" />
    </Route>
  </Switch>
)

export default MyFavorites
