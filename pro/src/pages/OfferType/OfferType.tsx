import React from 'react'

import { AppLayout } from 'app/AppLayout'
import OfferTypeScreen from 'screens/OfferType'

const OfferType = (): JSX.Element => {
  return (
    <AppLayout layout={'sticky-actions'}>
      <OfferTypeScreen />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OfferType
