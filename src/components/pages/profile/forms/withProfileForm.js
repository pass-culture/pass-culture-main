import React from 'react'
import ProfilFormContainer from './ProfileFormContainer'

const noop = () => {}

const withProfileForm = (
  WrappedComponent,
  config = {
    routeMethod: 'PATCH',
    routePath: 'users/current',
    stateKey: 'users',
  },
  initialValues = false,
  validator = noop
) => props => (
  <ProfilFormContainer
    WrappedComponent={WrappedComponent}
    config={config}
    initialValues={initialValues}
    validator={validator}
    {...props}
  />
)

export default withProfileForm
