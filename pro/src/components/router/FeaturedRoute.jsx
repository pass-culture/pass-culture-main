import PropTypes from 'prop-types'
import React from 'react'
import { useSelector } from 'react-redux'
import { Route } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import Spinner from 'components/layout/Spinner'
import NotMatch from 'components/pages/Errors/NotFound/NotFound'
import { selectFeaturesInitialized } from 'store/features/selectors'

const FeaturedRoute = props => {
  const { children, featureName, ...routeProps } = props
  const { path } = routeProps

  const isFeaturesInitialized = useSelector(selectFeaturesInitialized)
  const isActive = useActiveFeature(featureName)

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

FeaturedRoute.defaultProps = {
  children: null,
  featureName: null,
}

FeaturedRoute.propTypes = {
  children: PropTypes.node,
  featureName: PropTypes.string,
}

export default FeaturedRoute
