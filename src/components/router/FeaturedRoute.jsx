/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React from 'react'
import { useSelector } from 'react-redux'
import { Route } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import Spinner from 'components/layout/Spinner'
import NotMatch from 'components/pages/Errors/NotFound/NotFound'
import { featuresInitialized } from 'store/features/selectors'

const FeaturedRoute = props => {
  const { children, featureName, ...routeProps } = props
  const { path } = routeProps

  const featuresAreInitialized = useSelector(featuresInitialized)
  const isActive = useActiveFeature(featureName)

  if (!featuresAreInitialized) {
    return (
      <main className="spinner-container">
        <Spinner />
      </main>
    )
  }

  if (!isActive) {
    return (
      <Route
        component={NotMatch}
        path={path}
      />
    )
  }

  return (
    <Route {...routeProps}>
      {children || null}
    </Route>
  )
}

FeaturedRoute.defaultProps = {
  featureName: null,
}

FeaturedRoute.propTypes = {
  children: PropTypes.shape().isRequired,
  featureName: PropTypes.string,
}

export default FeaturedRoute
