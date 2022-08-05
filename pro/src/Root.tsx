import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'

import { AppRouter } from 'app'
import AppContainer from 'app/AppContainer'
import NavigationLogger from 'components/router/NavigationLogger'
import UtmTracking from 'components/router/UtmTracker'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import configureStore from 'store'

const { store } = configureStore()

const Root = (): JSX.Element => {
  return (
    <Provider store={store}>
      <AnalyticsContextProvider>
        <BrowserRouter>
          <AppContainer>
            <NavigationLogger />
            <UtmTracking />
            <AppRouter />
          </AppContainer>
        </BrowserRouter>
      </AnalyticsContextProvider>
    </Provider>
  )
}

export default Root
