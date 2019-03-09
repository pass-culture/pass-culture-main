/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import queryString from 'query-string'
import React from 'react'
import { Switch, Route } from 'react-router-dom'

import NotMatch from './NotMatch'
import RequestEmailForm from './forgot-password/RequestEmailForm'
import ResetThePasswordForm from './forgot-password/ResetThePasswordForm'
import SuccessView from './forgot-password/SuccessView'

const ForgotPasswordPage = ({ location }) => {
  const { token } = queryString.parse(location.search)
  return (
    <div id="forgot-password-page" className="page pc-gradient is-relative">
      <Switch location={location}>
        <Route
          exact
          path="/mot-de-passe-perdu/success"
          key="forgot-password-success-view"
          render={routeProps => (
            // si token -> affiche le form success pour le confirm
            // sinon -> affiche le form success pour le request
            <SuccessView {...routeProps} token={token} />
          )}
        />
        <Route
          exact
          path="/mot-de-passe-perdu"
          key="forgot-password-form-view"
          render={routeProps => {
            const initialValues = { token }
            const FormComponent = !token
              ? RequestEmailForm
              : ResetThePasswordForm
            return (
              <FormComponent {...routeProps} initialValues={initialValues} />
            )
          }}
        />
        <Route
          component={routeProps => (
            <NotMatch {...routeProps} delay={3} redirect="/connexion" />
          )}
        />
      </Switch>
    </div>
  )
}

ForgotPasswordPage.propTypes = {
  location: PropTypes.object.isRequired,
}

export default ForgotPasswordPage
