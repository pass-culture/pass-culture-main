import React from 'react'
import { Redirect, Route, Switch } from 'react-router-dom'

import Error from './Error'
import InvalidLink from './InvalidLink'
import PasswordFormContainer from './PasswordForm/PasswordFormContainer'

const Activation = () => (
  <div
    className="is-full-layout is-relative pc-gradient is-white-text flex-rows"
    id="activation-page"
  >
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
  </div>
)

export default Activation
