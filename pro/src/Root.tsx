import React from 'react'
import { BrowserRouter } from 'react-router-dom'

import { AppRouter } from 'app'
import AppContainer from 'app/AppContainer'
import NavigationLogger from 'components/router/NavigationLogger'
import UtmTracking from 'components/router/UtmTracker'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import StoreProvider from 'store/StoreProvider/StoreProvider'

const Root = (): JSX.Element => {
  return (
    <StoreProvider>
      <BrowserRouter>
        <AnalyticsContextProvider>
          <AppContainer>
            <NavigationLogger />
            <UtmTracking />
            <AppRouter />
          </AppContainer>
        </AnalyticsContextProvider>
      </BrowserRouter>
    </StoreProvider>
  )
}

export default Root
