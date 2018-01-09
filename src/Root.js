import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Redirect, Route } from 'react-router-dom'

import App from './App'
import ActivitiesPage from './pages/ActivitiesPage'
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
            render={() => <Redirect to='/spreadsheet' />}
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
