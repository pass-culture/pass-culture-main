import { Outlet } from 'react-router'

import { Layout } from 'app/App/layout/Layout'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'

import { SignupUnavailable } from './SignupUnavailable/SignupUnavailable'

export const Signup = () => {
  const isProAccountCreationEnabled = useActiveFeature(
    'ENABLE_PRO_ACCOUNT_CREATION'
  )
  const is2025SignUpEnabled = useActiveFeature('WIP_2025_SIGN_UP')

  return (
    <Layout layout={is2025SignUpEnabled ? 'sign-up' : 'logged-out'}>
      {isProAccountCreationEnabled ? <Outlet /> : <SignupUnavailable />}
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Signup
