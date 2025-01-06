import { Provider } from 'react-redux'

import { AppRouter } from 'app/AppRouter/AppRouter'
import { createStore } from 'commons/store/store'
import { StoreProvider } from 'commons/store/StoreProvider/StoreProvider'
import { PageTitleAnnouncer } from 'components/PageTitleAnnouncer/PageTitleAnnouncer'

interface RootProps {
  isAdageIframe: boolean
}

export const Root = ({ isAdageIframe }: RootProps): JSX.Element => {
  const { store } = createStore()

  return (
    <Provider store={store}>
      <StoreProvider isAdageIframe={isAdageIframe}>
        <AppRouter />
        <PageTitleAnnouncer />
      </StoreProvider>
    </Provider>
  )
}
