/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Route, Switch } from 'react-router-dom'

import ActivationPasswordForm from './password'

const ActivationPage = () => (
  <div
    id="activation-page"
    className="page is-relative pc-gradient is-white-text flex-rows"
  >
    <Switch>
      <Route path="/activation/:token" component={ActivationPasswordForm} />
    </Switch>
  </div>
)

export default ActivationPage
