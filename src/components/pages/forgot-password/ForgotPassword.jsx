import PropTypes from 'prop-types'
import { parse } from 'query-string'
import React from 'react'
import { Route, Switch } from 'react-router-dom'

import NotMatchContainer from '../not-match/NotMatchContainer'
import RequestEmailForm from './RequestEmailForm/RequestEmailForm'
import ResetThePasswordForm from './ResetPasswordForm/ResetPasswordForm'
import SuccessView from './SuccessView/SuccessView'

const ForgotPassword = ({ location }) => {
  const { token } = parse(location.search)
  const initialValues = { token }
  const FormComponent = !token ? RequestEmailForm : ResetThePasswordForm

  return (
    <main className="logout-form-main">
      <Switch>
        <Route
          exact
          path="/mot-de-passe-perdu/succes"
        >
          <SuccessView token={token} />
        </Route>
        <Route
          exact
          path="/mot-de-passe-perdu"
        >
          <FormComponent initialValues={initialValues} />
        </Route>
        <Route>
          <NotMatchContainer />
        </Route>
      </Switch>
    </main>
  )
}

ForgotPassword.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default ForgotPassword
