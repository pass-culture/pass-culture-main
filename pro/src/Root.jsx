import React, { useEffect, useState } from 'react'
import { Provider, useSelector } from 'react-redux'
import { BrowserRouter, Redirect, Route, Switch } from 'react-router-dom'

import AppContainer from 'app/AppContainer'
import AppLayout from 'app/AppLayout'
import useActiveFeature from 'components/hooks/useActiveFeature'
import Spinner from 'components/layout/Spinner'
import NotFound from 'components/pages/Errors/NotFound/NotFound'
import NavigationLogger from 'components/router/NavigationLogger'
import UtmTracking from 'components/router/UtmTracker'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import configureStore from 'store'
import {
  selectActiveFeatures,
  selectFeaturesInitialized,
} from 'store/features/selectors'
import routes, { routesWithoutLayout } from 'utils/routes_map'

const { store } = configureStore()

const Root = () => {
  return (
    <Provider store={store}>
      <AnalyticsContextProvider>
        <BrowserRouter>
          <AppContainer>
            <NavigationLogger />
            <UtmTracking />
            <AppRouter />
          </AppContainer>
        </BrowserRouter>
      </AnalyticsContextProvider>
    </Provider>
  )
}

const AppRouter = () => {
  const isFeaturesInitialized = useSelector(selectFeaturesInitialized)
  const activeFeatures = useSelector(selectActiveFeatures)
  const [activeRoutes, setActiveRoutes] = useState([])
  const [activeRoutesWithoutLayout, setActiveRoutesWithoutLayout] = useState([])
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

  if (!isFeaturesInitialized) {
    return (
      <main className="spinner-container">
        <Spinner />
      </main>
    )
  }

  return (
    <Switch>
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
        <Route exact={route.exact} key={route.path} path={route.path}>
          <AppLayout layoutConfig={route.meta && route.meta.layoutConfig}>
            <route.component />
          </AppLayout>
        </Route>
      ))}
      {activeRoutesWithoutLayout.map(route => (
        <Route {...route} exact={route.exact} key={route.path} />
      ))}
      <Route component={NotFound} />
    </Switch>
  )
}

export default Root
