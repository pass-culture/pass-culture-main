import React from 'react'
import { BrowserRouter } from 'react-router-dom'

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
            {/* The StrictMode component has been moved here to upgrade React 18 before React Router */}
            {/* TODO When React Router is upgraded to 6.0 we can move it back to the top of the React component tree */}
            {/* https://blog.devgenius.io/upgrade-to-react-18-issues-and-resolution-4838df8322b1 */}
            <React.StrictMode>
              <App>
                <>
                  <AppRouter />
                  <Notification />
                </>
              </App>
            </React.StrictMode>
          </BrowserRouter>
        </RemoteContextProvider>
      </AnalyticsContextProvider>
    </StoreProvider>
  )
}

export default Root
