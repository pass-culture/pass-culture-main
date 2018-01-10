import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Route } from 'react-router-dom'

import App from './App'
import ActivitiesPage from './pages/ActivitiesPage'
import ClientHomePage from './pages/ClientHomePage'
import ClientOfferPage from './pages/ClientOfferPage'
import SpreadsheetPage from './pages/SpreadsheetPage'
import WelcomePage from './pages/WelcomePage'
import store from './utils/store'

const Root = () => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <App>
          <Route exact
            path='/'
            render={() => <ClientHomePage />}
          />
          <Route exact
            path='/offers/:offerId'
            render={() => <ClientOfferPage />}
          />
          <Route exact
            path='/activities'
            render={() => <ActivitiesPage />}
          />
          <Route exact
            path='/spreadsheet'
            render={() => <SpreadsheetPage />}
          />
          <Route exact
            path='/welcome'
            render={() => <WelcomePage />}
          />
        </App>
      </BrowserRouter>
    </Provider>
  )
}

export default Root
