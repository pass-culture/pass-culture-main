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
  validator = noop
) => props => (
  <ProfilFormContainer
    WrappedComponent={WrappedComponent}
    config={config}
    validator={validator}
    {...props}
  />
)

export default withProfileForm
