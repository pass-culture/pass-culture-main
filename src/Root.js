import React from 'react'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { BrowserRouter, Route, Switch } from 'react-router-dom'

import App from './App'
import routes from './utils/routes'
import { configureStore } from './utils/store'
import NotMatch from './components/pages/NotMatch'
import { getReactRoutes } from './utils/routes-utils'

const { store, persistor } = configureStore()
const applicationRoutes = getReactRoutes(routes).filter(o => o)

const Root = () => (
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <BrowserRouter>
        <App>
          <Switch>
            {applicationRoutes.map(obj => (
              <Route {...obj} key={obj.path} />
            ))}
            <Route component={NotMatch} />
          </Switch>
        </App>
      </BrowserRouter>
    </PersistGate>
  </Provider>
)

export default Root
