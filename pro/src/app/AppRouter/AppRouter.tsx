import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { Redirect, Route, Switch } from 'react-router'

import AppLayout from 'app/AppLayout'
import useActiveFeature from 'components/hooks/useActiveFeature'
import NotFound from 'components/pages/Errors/NotFound/NotFound'
import { Logout } from 'routes/Logout'
import routes, { IRoute, routesWithoutLayout } from 'routes/routes_map'
import { selectActiveFeatures } from 'store/features/selectors'

const AppRouter = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)
  const [activeRoutes, setActiveRoutes] = useState<IRoute[]>([])
  const [activeRoutesWithoutLayout, setActiveRoutesWithoutLayout] = useState<
    IRoute[]
  >([])
  const useSummaryPage = useActiveFeature('OFFER_FORM_SUMMARY_PAGE')

  useEffect(() => {
    setActiveRoutes(
      routes.filter(
        route =>
          !route.featureName || activeFeatures.includes(route.featureName)
      )
    )

    setActiveRoutesWithoutLayout(
      routesWithoutLayout.filter(
        route =>
          !route.featureName || activeFeatures.includes(route.featureName)
      )
    )
  }, [activeFeatures])

  return (
    <Switch>
      <Route exact key="logout" path="/logout">
        <Logout />
      </Route>
      <Redirect
        from="/offres/:offerId([A-Z0-9]+)/edition"
        to={
          useSummaryPage
            ? '/offre/:offerId([A-Z0-9]+)/individuel/recapitulatif'
            : '/offre/:offerId([A-Z0-9]+)/individuel/edition'
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
