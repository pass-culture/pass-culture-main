import { AppRouter } from 'app/AppRouter/AppRouter'
import { StoreProvider } from 'commons/store/StoreProvider/StoreProvider'
import { createStore } from 'commons/store/store'
import { PageTitleAnnouncer } from 'components/PageTitleAnnouncer/PageTitleAnnouncer'
import { Provider } from 'react-redux'

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
