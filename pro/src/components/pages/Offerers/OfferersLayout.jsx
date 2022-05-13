import { Route, Switch, useRouteMatch } from 'react-router-dom'

import NotFound from 'components/pages/Errors/NotFound/NotFound'
import OffererCreation from './OffererCreation'
import OffererDetailsLayout from './Offerer/OffererDetailsLayout'
import OfferersContainer from './List/OfferersContainer'
import React from 'react'

const OfferersLayout = () => {
  const match = useRouteMatch()

  return (
    <Switch>
      <Route exact path={match.path}>
        <OfferersContainer />
      </Route>
      <Route exact path={`${match.path}/creation`}>
        <OffererCreation />
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
