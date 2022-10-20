import React from 'react'
import { BrowserRouter } from 'react-router-dom'

import { App, AppRouter } from 'app'
import Notification from 'components/layout/Notification/Notification'
import NavigationLogger from 'components/router/NavigationLogger'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import StoreProvider from 'store/StoreProvider/StoreProvider'

import { RemoteAnalyticsContextProvider } from './context/remoteConfigContext'

const Root = (): JSX.Element => {
  return (
    <StoreProvider>
      <AnalyticsContextProvider>
        <RemoteAnalyticsContextProvider>
          <BrowserRouter>
            <NavigationLogger />
            <App>
              <>
                <AppRouter />
                <Notification />
              </>
            </App>
          </BrowserRouter>
        </RemoteAnalyticsContextProvider>
      </AnalyticsContextProvider>
    </StoreProvider>
  )
}

export default Root
