/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Redirect, Route, Switch } from 'react-router-dom'

import ActivationEvents from './events'
import ActivationPasswordForm from './password'
import ActivationError from './ActivationError'

const ActivationPage = () => (
  <div
    id="activation-page"
    className="page is-relative pc-gradient is-white-text flex-rows"
  >
    <Switch>
      <Route path="/activation/error" component={ActivationError} exact />
      <Route path="/activation/events" component={ActivationEvents} exact />
      <Route path="/activation/:token" component={ActivationPasswordForm} />
      <Redirect to="/connexion" />
    </Switch>
  </div>
)

export default ActivationPage
