import React from 'react'
import { Route, Switch, useLocation, useParams } from 'react-router'

import { subRoutesOfferIndividualWizard } from 'app/AppRouter/routes_map'
import { OfferIndividualContextProvider } from 'context/OfferIndividualContext'
import useCurrentUser from 'hooks/useCurrentUser'
import { parse } from 'utils/query-string'

const OfferIndividualWizard = () => {
  const { currentUser } = useCurrentUser()
  const { offerId } = useParams<{ offerId: string }>()
  const { search } = useLocation()
  const { structure: offererId } = parse(search)
  return (
    <OfferIndividualContextProvider
      isUserAdmin={currentUser.isAdmin}
      offerId={offerId === 'creation' ? undefined : offerId}
      queryOffererId={offererId}
    >
      <Switch>
        {subRoutesOfferIndividualWizard.map(route => (
          <Route
            exact={route.exact}
            key={Array.isArray(route.path) ? route.path.join('|') : route.path}
            path={route.path}
          >
            <route.component />
          </Route>
        ))}
      </Switch>
    </OfferIndividualContextProvider>
  )
}

export default OfferIndividualWizard
