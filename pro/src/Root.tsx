import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import { CompatRouter } from 'react-router-dom-v5-compat'

import { App, AppRouter } from 'app'
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
            {/* Temporary router for react-router v6 migration */}
            {/* https://www.npmjs.com/package/react-router-dom-v5-compat */}
            <CompatRouter>
              <App>
                <>
                  <AppRouter />
                  <Notification />
                </>
              </App>
            </CompatRouter>
          </BrowserRouter>
        </RemoteContextProvider>
      </AnalyticsContextProvider>
    </StoreProvider>
  )
}

export default Root
