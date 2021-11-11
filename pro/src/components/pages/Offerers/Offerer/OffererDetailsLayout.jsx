/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import React from 'react'
import { Route, Switch, useRouteMatch } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import NotFound from 'components/pages/Errors/NotFound/NotFound'

import OffererDetailsContainer from './OffererDetails/OffererDetailsContainer'
import VenueLayout from './Venue/VenueLayout'
import VenueV1Layout from './VenueV1/VenueLayout'

const OffererDetailsLayout = () => {
  const match = useRouteMatch()
  const isVenueV2Enabled = useActiveFeature('ENABLE_NEW_VENUE_PAGES')

  return (
    <Switch>
      <Route
        exact
        path={`${match.path}`}
      >
        <OffererDetailsContainer />
      </Route>
      <Route path={`${match.path}/lieux`}>
        {isVenueV2Enabled ? <VenueLayout /> : <VenueV1Layout />}
      </Route>
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

export default OffererDetailsLayout
