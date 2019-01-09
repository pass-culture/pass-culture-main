/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Redirect, Route, Switch } from 'react-router-dom'

import ActivationError from './error'
import ActivationEvents from './events'
import ActivationPasswordForm from './password'

const ActivationPage = () => (
  <div
    id="activation-page"
    className="is-full-layout is-relative pc-gradient is-white-text flex-rows"
  >
    <Switch>
      <Route path="/activation/error" component={ActivationError} exact />
      <Route path="/activation/events" component={ActivationEvents} exact />
      <Route path="/activation/:token" component={ActivationPasswordForm} />
      <Redirect to="/activation/error" />
    </Switch>
  </div>
)

export default ActivationPage
