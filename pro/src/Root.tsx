import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Provider } from 'react-redux'

import { AppRouter } from 'app/AppRouter'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import createStore from 'store/store'
import StoreProvider from 'store/StoreProvider/StoreProvider'

import { RemoteContextProvider } from './context/remoteConfigContext'

interface RootProps {
  isAdageIframe: boolean
}

const Root = ({ isAdageIframe }: RootProps): JSX.Element => {
  const { store } = createStore()

  const queryClient = new QueryClient()

  return (
    <Provider store={store}>
      <AnalyticsContextProvider>
        <RemoteContextProvider>
          <StoreProvider isAdageIframe={isAdageIframe}>
            <QueryClientProvider client={queryClient}>
              <AppRouter />
            </QueryClientProvider>
          </StoreProvider>
        </RemoteContextProvider>
      </AnalyticsContextProvider>
    </Provider>
  )
}

// This is used in the main index.jsx file
// ts-unused-exports:disable-next-line
export default Root
