import { Route, Switch, useRouteMatch } from 'react-router-dom'

import NotFound from 'components/pages/Errors/NotFound/NotFound'
import React from 'react'
import VenueCreation from './VenueCreation/VenueCreation'
import VenueEdition from './VenueEdition/VenueEdition'

const VenueLayout = () => {
  const match = useRouteMatch()
  return (
    <Switch>
      <Route exact path={`${match.path}/creation`}>
        <VenueCreation />
      </Route>
      <Route exact path={`${match.path}/:venueId([A-Z0-9]+)`}>
        <VenueEdition />
      </Route>
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

export default VenueLayout
