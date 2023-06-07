import React from 'react'

import { AppRouter } from 'app/AppRouter'
import routes from 'app/AppRouter/routesMap'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import StoreProvider from 'store/StoreProvider/StoreProvider'

import { RemoteContextProvider } from './context/remoteConfigContext'

const Root = (): JSX.Element => {
  return (
    <StoreProvider>
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
