import React from 'react'
import { Provider } from 'react-redux'

import { AppRouter } from 'app/AppRouter/AppRouter'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import createStore from 'store/store'
import StoreProvider from 'store/StoreProvider/StoreProvider'

interface RootProps {
  isAdageIframe: boolean
}

const Root = ({ isAdageIframe }: RootProps): JSX.Element => {
  const { store } = createStore()

  return (
    <Provider store={store}>
      <AnalyticsContextProvider>
        <StoreProvider isAdageIframe={isAdageIframe}>
          <AppRouter />
        </StoreProvider>
      </AnalyticsContextProvider>
    </Provider>
  )
}

// This is used in the main index.jsx file
// ts-unused-exports:disable-next-line
export default Root
