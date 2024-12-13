import { Provider } from 'react-redux'
// @ts-expect-error no types for this lib yet
import { WonderPush } from 'react-wonderpush'

import { AppRouter } from 'app/AppRouter/AppRouter'
import { createStore } from 'commons/store/store'
import { StoreProvider } from 'commons/store/StoreProvider/StoreProvider'
import { WONDER_PUSH_WEB_KEY } from 'commons/utils/config'
import { PageTitleAnnouncer } from 'components/PageTitleAnnouncer/PageTitleAnnouncer'

interface RootProps {
  isAdageIframe: boolean
}

export const Root = ({ isAdageIframe }: RootProps): JSX.Element => {
  const { store } = createStore()

  return (
    <WonderPush options={{ webKey: WONDER_PUSH_WEB_KEY }}>
      <Provider store={store}>
        <StoreProvider isAdageIframe={isAdageIframe}>
          <AppRouter />
          <PageTitleAnnouncer />
        </StoreProvider>
      </Provider>
    </WonderPush>
  )
}
