import React from 'react'
import { Provider } from 'react-redux'

import { AppRouter } from 'app/AppRouter/AppRouter'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import createStore from 'store/store'
import StoreProvider from 'store/StoreProvider/StoreProvider'

import { RemoteContextProvider } from './context/remoteConfigContext'

interface RootProps {
  isAdageIframe: boolean
}

const Root = ({ isAdageIframe }: RootProps): JSX.Element => {
  const { store } = createStore()

  return (
    <Provider store={store}>
      <AnalyticsContextProvider>
        <RemoteContextProvider>
          <StoreProvider isAdageIframe={isAdageIframe}>
            <AppRouter />
          </StoreProvider>
        </RemoteContextProvider>
      </AnalyticsContextProvider>
    </Provider>
  )
}

// This is used in the main index.jsx file
// ts-unused-exports:disable-next-line
export default Root
