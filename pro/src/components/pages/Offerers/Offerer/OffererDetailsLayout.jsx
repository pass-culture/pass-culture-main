import { Route, Switch, useRouteMatch } from 'react-router-dom'

import BusinessUnitList from 'routes/BusinessUnitList'
import NotFound from 'components/pages/Errors/NotFound/NotFound'
import OffererDetailsContainer from './OffererDetails/OffererDetailsContainer'
import React from 'react'
import VenueV1Layout from './VenueV1/VenueLayout'
import useActiveFeature from 'components/hooks/useActiveFeature'

const OffererDetailsLayout = () => {
  const match = useRouteMatch()
  const isEnforceBankInfoWithSiretEnabled = useActiveFeature(
    'ENFORCE_BANK_INFORMATION_WITH_SIRET'
  )
  return (
    <Switch>
      <Route exact path={`${match.path}`}>
        <OffererDetailsContainer match={match} />
      </Route>
      <Route path={`${match.path}/lieux`}>
        <VenueV1Layout />
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
