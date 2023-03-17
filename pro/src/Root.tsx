import React from 'react'

import { AppRouter } from 'app'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import StoreProvider from 'store/StoreProvider/StoreProvider'

import { RemoteContextProvider } from './context/remoteConfigContext'

const Root = (): JSX.Element => {
  return (
    <StoreProvider>
      <AnalyticsContextProvider>
        <RemoteContextProvider>
          <AppRouter />
        </RemoteContextProvider>
      </AnalyticsContextProvider>
    </StoreProvider>
  )
}

export default Root
