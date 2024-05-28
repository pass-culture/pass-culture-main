import React from 'react'
import { Provider } from 'react-redux'

import { AppRouter } from 'app/AppRouter/AppRouter'
import { createStore } from 'store/store'
import { StoreProvider } from 'store/StoreProvider/StoreProvider'

interface RootProps {
  isAdageIframe: boolean
}

export const Root = ({ isAdageIframe }: RootProps): JSX.Element => {
  const { store } = createStore()

  return (
    <Provider store={store}>
      <StoreProvider isAdageIframe={isAdageIframe}>
        <AppRouter />
      </StoreProvider>
    </Provider>
  )
}
