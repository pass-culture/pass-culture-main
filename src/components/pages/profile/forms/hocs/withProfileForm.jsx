import React from 'react'
import ProfilFormContainer from '../ProfileFormContainer'

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
    config={config}
    validator={validator}
    WrappedComponent={WrappedComponent}
    {...props}
  />
)

export default withProfileForm
