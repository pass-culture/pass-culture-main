import React from 'react'
import { Route, Switch, useRouteMatch } from 'react-router-dom'

import NotFound from 'components/pages/Errors/NotFound/NotFound'

import VenueCreationContainer from 'components/pages/Venue/VenueCreation/VenueCreationContainer'
import VenueEditionContainer from 'components/pages/Venue/VenueEdition/VenueEditionContainer'

const VenueLayout = () => {
  const match = useRouteMatch()
  return (
    <Switch>
      <Route
        exact
        path={`${match.path}/creation`}
      >
        <VenueCreationContainer />
      </Route>
      <Route
        exact
        path={`${match.path}/:venueId([A-Z0-9]+)`}
      >
        <VenueEditionContainer />
      </Route>
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

export default VenueLayout
