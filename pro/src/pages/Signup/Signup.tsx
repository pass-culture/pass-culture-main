import { Outlet, useLocation } from 'react-router'

import { SignUpLayout } from '@/app/App/layouts/logged-out/SignUpLayout/SignUpLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'

import { SignupUnavailable } from './SignupUnavailable/SignupUnavailable'

export const Signup = () => {
  const isProAccountCreationEnabled = useActiveFeature(
    'ENABLE_PRO_ACCOUNT_CREATION'
  )

  const location = useLocation()

  const mainHeadingsMap = new Map([
    ['/inscription/compte/creation', 'Créez votre compte'],
    ['/inscription/compte/confirmation', 'Validez votre adresse email'],
  ])

  const mainHeading = mainHeadingsMap.get(location.pathname)

  return (
    <SignUpLayout mainHeading={mainHeading}>
      {isProAccountCreationEnabled ? <Outlet /> : <SignupUnavailable />}
    </SignUpLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Signup
