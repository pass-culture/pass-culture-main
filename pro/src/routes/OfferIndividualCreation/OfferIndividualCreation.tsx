import React from 'react'
import { Switch, Route, useRouteMatch } from 'react-router-dom'

import { OfferIndividual as OfferIndividualScreen } from 'screens/OfferIndividual'
import { Informations as InformationsRoute } from './Informations'
import { Venue as VenueRoute } from './Venue'

const OfferIndividualCreation = (): JSX.Element => {
  const match = useRouteMatch()

  return (
    <div>
      <h1 style={{ color: 'red' }}>Route: OfferIndividualCreation</h1>
      <OfferIndividualScreen>
        <Switch>
          <Route path={`${match.path}/informations`}>
            <InformationsRoute />
          </Route>
          <Route path={`${match.path}/lieu`}>
            <VenueRoute />
          </Route>
        </Switch>
      </OfferIndividualScreen>
    </div>
  )
}

export default OfferIndividualCreation
