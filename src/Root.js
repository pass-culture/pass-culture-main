import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Route } from 'react-router-dom'

import App from './App'
import ActivitiesPage from './pages/ActivitiesPage'
import ClientCreateProfilePage from './pages/ClientCreateProfilePage'
import ClientHomePage from './pages/ClientHomePage'
import ClientOfferPage from './pages/ClientOfferPage'
import ProfessionalHomePage from './pages/ProfessionalHomePage'
import WelcomePage from './pages/WelcomePage'
import store from './utils/store'

const Root = () => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <App>
          <Route exact
            path='/'
            render={() => <ClientCreateProfilePage />} />
          <Route exact
            path='/offres'
            render={() => <ClientHomePage />} />
          <Route exact
            path='/offres/:offerId'
            render={() => <ClientOfferPage />} />
          <Route exact
            path='/activities'
            render={() => <ActivitiesPage />} />
          <Route exact
            path='/gestion'
            render={() => <ProfessionalHomePage />} />
          <Route exact
            path='/welcome'
            render={() => <WelcomePage />} />
        </App>
      </BrowserRouter>
    </Provider>
  )
}

export default Root
