import React from 'react'

import { Layout } from 'app/App/layout/Layout'

import { OfferTypeScreen } from './OfferType/OfferType'

const OfferType = (): JSX.Element => {
  return (
    <Layout layout="sticky-actions">
      <OfferTypeScreen />
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OfferType
