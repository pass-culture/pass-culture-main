import React from 'react'
import { BrowserRouter } from 'react-router-dom'

import { App, AppRouter } from 'app'
import { AppContextProvider } from 'app/AppContext/AppContext'
import Notification from 'components/Notification/Notification'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import StoreProvider from 'store/StoreProvider/StoreProvider'

import { RemoteContextProvider } from './context/remoteConfigContext'

const Root = (): JSX.Element => {
  return (
    <StoreProvider>
      <AnalyticsContextProvider>
        <RemoteContextProvider>
          <BrowserRouter>
            <AppContextProvider>
              <App>
                <>
                  <AppRouter />
                  <Notification />
                </>
              </App>
            </AppContextProvider>
          </BrowserRouter>
        </RemoteContextProvider>
      </AnalyticsContextProvider>
    </StoreProvider>
  )
}

export default Root
