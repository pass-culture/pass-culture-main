import React from 'react'
import { useLocation } from 'react-router-dom'

import { Layout } from 'app/App/layout/Layout'

import { OfferTypeScreen } from './OfferType/OfferType'

export const OfferType = (): JSX.Element => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1

  return (
    <Layout layout={isOnboarding ? 'sticky-onboarding' : 'sticky-actions'}>
      <OfferTypeScreen />
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OfferType
