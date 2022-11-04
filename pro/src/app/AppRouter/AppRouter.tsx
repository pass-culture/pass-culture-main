import React from 'react'
import { useSelector } from 'react-redux'
import { Redirect, Route, Switch } from 'react-router'

import AppLayout from 'app/AppLayout'
import useActiveFeature from 'hooks/useActiveFeature'
import NotFound from 'pages/Errors/NotFound/NotFound'
import { Logout } from 'pages/Logout'
import routes, { routesWithoutLayout } from 'routes/routes_map'
import { selectActiveFeatures } from 'store/features/selectors'

const AppRouter = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)
  const activeRoutes = routes.filter(
    route => !route.featureName || activeFeatures.includes(route.featureName)
  )
  const activeRoutesWithoutLayout = routesWithoutLayout.filter(
    route => !route.featureName || activeFeatures.includes(route.featureName)
  )
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')

  return (
    <Switch>
      <Route exact key="logout" path="/logout">
        <Logout />
      </Route>
      <Redirect
        from="/offres/:offerId([A-Z0-9]+)/edition"
        to={
          isOfferFormV3
            ? '/offre/:offerId([A-Z0-9]+)/v3/individuelle/recapitulatif'
            : '/offre/:offerId([A-Z0-9]+)/individuel/recapitulatif'
        }
      />
      <Redirect
        from="/offre/:offerId([A-Z0-9]+)/scolaire/edition"
        to="/offre/:offerId([A-Z0-9]+)/collectif/edition"
      />
      {activeRoutes.map(route => (
        <Route
          exact={route.exact}
          key={Array.isArray(route.path) ? route.path.join('|') : route.path}
          path={route.path}
        >
          <AppLayout layoutConfig={route.meta && route.meta.layoutConfig}>
            <route.component />
          </AppLayout>
        </Route>
      ))}
      {activeRoutesWithoutLayout.map(route => (
        <Route
          {...route}
          exact={route.exact}
          key={Array.isArray(route.path) ? route.path.join('|') : route.path}
        />
      ))}
      <Route component={NotFound} />
    </Switch>
  )
}

export default AppRouter
