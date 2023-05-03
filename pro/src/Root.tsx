import React from 'react'

import { AppRouter } from 'createReactApp'
import routes from 'createReactApp/AppRouter/routesMap'
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

export default Root
