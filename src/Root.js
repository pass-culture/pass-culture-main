import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Route } from 'react-router-dom'

import App from './App'
import ActivitiesPage from './pages/ActivitiesPage'
import ClientCreateProfilePage from './pages/ClientCreateProfilePage'
import ClientHomePage from './pages/ClientHomePage'
import ClientOfferPage from './pages/ClientOfferPage'
import InventoryPage from './pages/InventoryPage'
import OffererPage from './pages/OffererPage'
import ProfessionalHomePage from './pages/ProfessionalHomePage'
import ProfilePage from './pages/ProfilePage'
import SignPage from './pages/SignPage'
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
            path='/activities'
            render={() => <ActivitiesPage />} />
          <Route exact
            path='/explore'
            render={() => <ClientHomePage />} />
          <Route exact
            path='/gestion'
            render={() => <ProfessionalHomePage />} />
          <Route exact
            path='/gestion/:offererId'
            render={props => <OffererPage offererId={props.match.params.offererId} />} />
          <Route exact
            path='/inscription'
            render={() => <SignPage />} />
          <Route exact
            path='/inventaire'
            render={() => <InventoryPage />} />
          <Route exact
            path='/offres/:offerId'
            render={props => <ClientOfferPage offerId={props.match.params.offerId} />} />
          <Route exact
            path='/profile'
            render={() => <ProfilePage />} />
          <Route exact
            path='/welcome'
            render={() => <WelcomePage />} />
        </App>
      </BrowserRouter>
    </Provider>
  )
}

export default Root
