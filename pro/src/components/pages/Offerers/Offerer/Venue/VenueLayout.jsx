import { Route, Switch, useRouteMatch } from 'react-router-dom'

import NotFound from 'components/pages/Errors/NotFound/NotFound'
import React from 'react'
import VenueCreation from './VenueCreation/VenueCreation'
import VenueEdition from './VenueEdition/VenueEdition'

const VenueLayout = () => {
  const match = useRouteMatch()

  return (
    <Switch>
      <Route path={`${match.path}/creation`}>
        <VenueCreation />
      </Route>
      <Route path={`${match.path}/temporaire/creation`}>
        <VenueCreation isTemporary />
      </Route>
      <Route path={`${match.path}/:venueId([A-Z0-9]+)`}>
        <VenueEdition />
      </Route>
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

export default VenueLayout
