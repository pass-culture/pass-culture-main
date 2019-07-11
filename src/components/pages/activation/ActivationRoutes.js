import React from 'react'
import { Redirect, Route, Switch } from 'react-router-dom'

import ActivationError from './error/ActivationError'
import InvalidLink from './invalid-link/InvalidLink'
import ActivationPageContainer from './password/ActivationPageContainer'

const ActivationRoutes = () => (
  <div
    className="is-full-layout is-relative pc-gradient is-white-text flex-rows"
    id="activation-page"
  >
    <Switch>
      <Route
        component={ActivationError}
        exact
        path="/activation/error"
      />
      <Route
        component={InvalidLink}
        exact
        path="/activation/lien-invalide"
      />
      <Route
        component={ActivationPageContainer}
        path="/activation/:token"
      />
      <Redirect to="/activation/error" />
    </Switch>
  </div>
)

export default ActivationRoutes
