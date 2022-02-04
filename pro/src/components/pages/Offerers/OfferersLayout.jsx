import React from 'react'
import { Route, Switch, useRouteMatch } from 'react-router-dom'

import NotFound from 'components/pages/Errors/NotFound/NotFound'

import OfferersContainer from './List/OfferersContainer'
import OffererDetailsLayout from './Offerer/OffererDetailsLayout'
import OffererCreationContainer from './OffererCreation/OffererCreationContainer'

const OfferersLayout = () => {
  const match = useRouteMatch()

  return (
    <Switch>
      <Route exact path={match.path}>
        <OfferersContainer />
      </Route>
      <Route exact path={`${match.path}/creation`}>
        <OffererCreationContainer />
      </Route>
      <Route path={`${match.path}/:offererId([A-Z0-9]+)`}>
        <OffererDetailsLayout />
      </Route>
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

export default OfferersLayout
