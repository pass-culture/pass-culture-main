import { Outlet } from 'react-router'

import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'

import { SignupUnavailable } from './SignupUnavailable/SignupUnavailable'
export const Signup = () => {
  const isProAccountCreationEnabled = useActiveFeature(
    'ENABLE_PRO_ACCOUNT_CREATION'
  )

  return (
    <FullLayout>
      {isProAccountCreationEnabled ? <Outlet /> : <SignupUnavailable />}
    </FullLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Signup
