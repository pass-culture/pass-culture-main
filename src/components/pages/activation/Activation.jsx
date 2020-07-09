import React from 'react'
import { Redirect, Route, Switch } from 'react-router-dom'

import Error from './Error/Error'
import InvalidLink from './InvalidLink/InvalidLink'
import PasswordFormContainer from './PasswordForm/PasswordFormContainer'

const Activation = () => (
  <main className="logout-form-main">
    <Switch>
      <Route
        exact
        path="/activation/error"
      >
        <Error />
      </Route>
      <Route
        exact
        path="/activation/lien-invalide"
      >
        <InvalidLink />
      </Route>
      <Route
        exact
        path="/activation/:token([A-Z0-9]+)"
      >
        <PasswordFormContainer />
      </Route>
      <Redirect to="/activation/error" />
    </Switch>
  </main>
)

export default Activation
