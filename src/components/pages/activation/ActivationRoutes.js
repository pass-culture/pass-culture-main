import React from 'react'
import { Redirect, Route } from 'react-router-dom'

import ActivationError from './error'
import ActivationPageContainer from './password/ActivationPageContainer'

const ActivationRoutes = () => (
  <div
    id="activation-page"
    className="is-full-layout is-relative pc-gradient is-white-text flex-rows"
  >
    <Route path="/activation/error" component={ActivationError} exact />
    <Route path="/activation/:token" component={ActivationPageContainer} />
    <Redirect to="/activation/error" />
  </div>
)

export default ActivationRoutes
