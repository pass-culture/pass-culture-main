import React from 'react'
import { Route, Switch, useRouteMatch } from 'react-router-dom'

import NotFound from 'components/pages/Errors/NotFound/NotFound'

import OffererDetailsContainer from './OffererDetails/OffererDetailsContainer'
import VenueV1Layout from './VenueV1/VenueLayout'

const OffererDetailsLayout = () => {
  const match = useRouteMatch()
  return (
    <Switch>
      <Route
        exact
        path={`${match.path}`}
      >
        <OffererDetailsContainer />
      </Route>
      <Route path={`${match.path}/lieux`}>
        <VenueV1Layout />
      </Route>
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

export default OffererDetailsLayout
