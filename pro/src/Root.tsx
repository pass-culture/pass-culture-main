import React from 'react'
import { BrowserRouter } from 'react-router-dom'

import { App, AppRouter } from 'app'
import Notification from 'components/layout/Notification/Notification'
import NavigationLogger from 'components/router/NavigationLogger'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import StoreProvider from 'store/StoreProvider/StoreProvider'

import { RemoteContextProvider } from './context/remoteConfigContext'

const Root = (): JSX.Element => {
  return (
    <StoreProvider>
      <AnalyticsContextProvider>
        <RemoteContextProvider>
          <BrowserRouter>
            <NavigationLogger />
            <App>
              <>
                <AppRouter />
                <Notification />
              </>
            </App>
          </BrowserRouter>
        </RemoteContextProvider>
      </AnalyticsContextProvider>
    </StoreProvider>
  )
}

export default Root
