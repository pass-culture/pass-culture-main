import { Outlet, useLocation } from 'react-router'

import { Layout } from 'app/App/layout/Layout'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'

import { SignupUnavailable } from './SignupUnavailable/SignupUnavailable'

export const Signup = () => {
  const isProAccountCreationEnabled = useActiveFeature(
    'ENABLE_PRO_ACCOUNT_CREATION'
  )
  const is2025SignUpEnabled = useActiveFeature('WIP_2025_SIGN_UP')

  const location = useLocation()

  const mainHeadingsMap = new Map([
    ['/inscription/compte/creation', 'Créez votre compte'],
    ['/inscription/compte/confirmation', 'Validez votre adresse email'],
  ])

  const mainHeading = mainHeadingsMap.get(location.pathname)

  return (
    <Layout
      layout={is2025SignUpEnabled ? 'sign-up' : 'logged-out'}
      mainHeading={mainHeading}
    >
      {isProAccountCreationEnabled ? <Outlet /> : <SignupUnavailable />}
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Signup
