import React from 'react'
import { Route, Switch, useRouteMatch } from 'react-router-dom'

import NotFound from 'components/pages/Errors/NotFound/NotFound'
import FeaturedRoute from 'components/router/FeaturedRoute'
import { useFeature } from 'hooks'
import BusinessUnitList from 'routes/BusinessUnitList'

import OffererDetailsContainer from './OffererDetails/OffererDetailsContainer'
import VenueLayout from './Venue/VenueLayout'
import VenueV1Layout from './VenueV1/VenueLayout'

const OffererDetailsLayout = () => {
  const match = useRouteMatch()
  const { isActive: isVenueV2Enabled } = useFeature('ENABLE_NEW_VENUE_PAGES')

  return (
    <Switch>
      <Route exact path={`${match.path}`}>
        <OffererDetailsContainer />
      </Route>
      <Route path={`${match.path}/lieux`}>
        {isVenueV2Enabled ? <VenueLayout /> : <VenueV1Layout />}
      </Route>
      <FeaturedRoute
        featureName="ENFORCE_BANK_INFORMATION_WITH_SIRET"
        path={`${match.path}/point-de-remboursement`}
      >
        <BusinessUnitList />
      </FeaturedRoute>
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

export default OffererDetailsLayout
