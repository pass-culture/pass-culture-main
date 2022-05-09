import { Route, Switch, useRouteMatch } from 'react-router-dom'

import BusinessUnitList from 'routes/BusinessUnitList'
import NotFound from 'components/pages/Errors/NotFound/NotFound'
import OffererDetailsContainer from './OffererDetails/OffererDetailsContainer'
import React from 'react'
import VenueLayout from './Venue/VenueLayout'
import VenueV1Layout from './VenueV1/VenueLayout'
import useActiveFeature from 'components/hooks/useActiveFeature'

const OffererDetailsLayout = () => {
  const match = useRouteMatch()
  const isVenueV2Enabled = useActiveFeature('ENABLE_NEW_VENUE_PAGES')
  const isEnforceBankInfoWithSiretEnabled = useActiveFeature(
    'ENFORCE_BANK_INFORMATION_WITH_SIRET'
  )
  return (
    <Switch>
      <Route exact path={`${match.path}`}>
        <OffererDetailsContainer match={match} />
      </Route>
      <Route path={`${match.path}/lieux`}>
        {isVenueV2Enabled ? <VenueLayout /> : <VenueV1Layout />}
      </Route>
      {isEnforceBankInfoWithSiretEnabled && (
        <Route path={`${match.path}/point-de-remboursement`}>
          <BusinessUnitList />
        </Route>
      )}
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

export default OffererDetailsLayout
