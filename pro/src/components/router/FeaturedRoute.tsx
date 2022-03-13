import React from 'react'
import { useSelector } from 'react-redux'
import { Route } from 'react-router-dom'
import type { RouteProps } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import Spinner from 'components/layout/Spinner'
import NotMatch from 'components/pages/Errors/NotFound/NotFound'
import { selectFeaturesInitialized } from 'store/features/selectors'

interface IFeaturedRouteProps extends RouteProps {
  featureName?: string | null
}

const FeaturedRoute = (props: IFeaturedRouteProps): JSX.Element => {
  const { children, featureName, ...routeProps } = props
  const { path } = routeProps

  const isFeaturesInitialized = useSelector(selectFeaturesInitialized)
  const isActive = useActiveFeature(featureName || null)

  if (!isFeaturesInitialized) {
    return (
      <main className="spinner-container">
        <Spinner />
      </main>
    )
  }

  if (!isActive) {
    return <Route component={NotMatch} path={path} />
  }

  return <Route {...routeProps}>{children}</Route>
}

export default FeaturedRoute
