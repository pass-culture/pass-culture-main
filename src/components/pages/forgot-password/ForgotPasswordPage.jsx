import PropTypes from 'prop-types'
import queryString from 'query-string'
import React, { Component } from 'react'
import { Switch, Route } from 'react-router-dom'

import NotMatch from '../not-match/NotMatch'
import RequestEmailForm from './RequestEmailForm'
import ResetThePasswordForm from './ResetThePasswordForm'
import SuccessView from './SuccessView'

class ForgotPasswordPage extends Component {
  renderforgotPasswordSuccessViewRoute = token => routeProps => (
    // si token -> affiche le form success pour le confirm
    // sinon -> affiche le form success pour le request
    <SuccessView
      {...routeProps}
      token={token}
    />
  )

  renderforgotPasswordFormViewRoute = token => routeProps => {
    const initialValues = { token }
    const FormComponent = !token ? RequestEmailForm : ResetThePasswordForm
    return (<FormComponent
      {...routeProps}
      initialValues={initialValues}
            />)
  }

  renderDefaultRoute = routeProps => (<NotMatch
    {...routeProps}
    delay={3}
    redirect="/connexion"
                                      />)

  render() {
    const { location } = this.props
    const { token } = queryString.parse(location.search)
    return (
      <div
        className="page pc-gradient is-relative"
        id="forgot-password-page"
      >
        <Switch location={location}>
          <Route
            exact
            key="forgot-password-success-view"
            path="/mot-de-passe-perdu/success"
            render={this.renderforgotPasswordSuccessViewRoute(token)}
          />
          <Route
            exact
            key="forgot-password-form-view"
            path="/mot-de-passe-perdu"
            render={this.renderforgotPasswordFormViewRoute(token)}
          />
          <Route component={this.renderDefaultRoute} />
        </Switch>
      </div>
    )
  }
}

ForgotPasswordPage.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default ForgotPasswordPage
