import React, { StrictMode } from 'react'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { BrowserRouter, Route, Switch } from 'react-router-dom'

import App from './App'
import MatomoPageTracker from './components/matomo/MatomoPageTracker'
import NotMatch from './components/pages/NotMatch'
import routes from './utils/routes'
import { getReactRoutes } from './utils/routes-utils'
import { configureStore } from './utils/store'

const approutes = getReactRoutes(routes)
const { store, persistor } = configureStore()

const Root = () => (
  <StrictMode>
    <Provider store={store}>
      <PersistGate
        loading={null}
        persistor={persistor}
      >
        <BrowserRouter>
          <App>
            <Switch>
              {approutes && approutes.map(obj => obj && <Route
                {...obj}
                key={obj.path}
                                                        />)}
              <Route component={NotMatch} />
            </Switch>
            <MatomoPageTracker />
          </App>
        </BrowserRouter>
      </PersistGate>
    </Provider>
  </StrictMode>
)

export default Root
