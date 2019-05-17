import React from 'react'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { BrowserRouter, Route, Switch } from 'react-router-dom'

import App from './App'
import routes from './utils/routes'
import { configureStore } from './utils/store'
import NotMatch from './components/pages/NotMatch'
import { getReactRoutes } from './utils/routes-utils'
import MatomoTracker from './components/hocs/MatomoTracker'

const approutes = getReactRoutes(routes)
const { store, persistor } = configureStore()

const Root = () => (
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <BrowserRouter>
        <App>
          <Switch>
            {approutes &&
              approutes.map(obj => obj && <Route {...obj} key={obj.path} />)}
            <Route component={NotMatch} />
          </Switch>
        </App>
        <MatomoTracker />
      </BrowserRouter>
    </PersistGate>
  </Provider>
)

export default Root
