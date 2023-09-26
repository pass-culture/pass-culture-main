import React from 'react'

import { AppRouter } from 'app/AppRouter'
import routes from 'app/AppRouter/routesMap'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import StoreProvider from 'store/StoreProvider/StoreProvider'

import { RemoteContextProvider } from './context/remoteConfigContext'

interface RootProps {
  isAdageIframe: boolean
}

const Root = ({ isAdageIframe }: RootProps): JSX.Element => {
  return (
    <StoreProvider isAdageIframe={isAdageIframe}>
      <AnalyticsContextProvider>
        <RemoteContextProvider>
          <AppRouter routes={routes} />
        </RemoteContextProvider>
      </AnalyticsContextProvider>
    </StoreProvider>
  )
}

// This is used in the main index.jsx file
// ts-unused-exports:disable-next-line
export default Root
