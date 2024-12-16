import React from 'react'
import { Outlet } from 'react-router'

import { Layout } from 'app/App/layout/Layout'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'

import { SignupUnavailable } from './SignupUnavailable/SignupUnavailable'

export const Signup = () => {
  const isProAccountCreationEnabled = useActiveFeature(
    'ENABLE_PRO_ACCOUNT_CREATION'
  )
  return (
    <Layout layout="logged-out">
      {isProAccountCreationEnabled ? <Outlet /> : <SignupUnavailable />}
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Signup
