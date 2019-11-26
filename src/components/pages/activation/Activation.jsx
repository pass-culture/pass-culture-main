import React from 'react'
import { Redirect, Route, Switch } from 'react-router-dom'

import Error from './Error/Error'
import InvalidLink from './InvalidLink/InvalidLink'
import PasswordFormContainer from './PasswordForm/PasswordFormContainer'

const Activation = () => (
  <main className="logout-form-main">
    <Switch>
      <Route
        component={Error}
        exact
        path="/activation/error"
      />
      <Route
        component={InvalidLink}
        exact
        path="/activation/lien-invalide"
      />
      <Route
        component={PasswordFormContainer}
        path="/activation/:token"
      />
      <Redirect to="/activation/error" />
    </Switch>
  </main>
)

export default Activation
