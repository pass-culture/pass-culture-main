import PropTypes from 'prop-types'
import React from 'react'
import { Route, Switch } from 'react-router'

import NotMatch from '../not-match/NotMatch'
import ContactSaved from './ContactSaved/ContactSaved'
import EligibilityCheck from './EligibilityCheck/EligibilityCheck'
import Eligible from './Eligible/Eligible'
import EligibleSoon from './EligibleSoon/EligibleSoon'
import IneligibleDepartment from './IneligibleDepartment/IneligibleDepartment'
import IneligibleOverEighteen from './IneligibleOverEighteen/IneligibleOverEighteen'
import IneligibleUnderEighteen from './IneligibleUnderEighteen/IneligibleUnderEighteen'
import { useReCaptchaScript } from './utils/recaptcha'

const CreateAccount = ({ history, location, match }) => {
  useReCaptchaScript()

  return (
    <Switch>
      <Route
        exact
        path={`${match.path}/eligible`}
      >
        <Eligible />
      </Route>
      <Route
        exact
        path={`${match.path}/departement-non-eligible`}
      >
        <IneligibleDepartment />
      </Route>
      <Route
        exact
        path={`${match.path}/pas-eligible`}
      >
        <IneligibleOverEighteen />
      </Route>
      <Route
        exact
        path={`${match.path}/bientot`}
      >
        <EligibleSoon />
      </Route>
      <Route
        exact
        path={`${match.path}/trop-tot`}
      >
        <IneligibleUnderEighteen />
      </Route>
      <Route
        exact
        path={`${match.path}/gardons-contact`}
      >
        <ContactSaved />
      </Route>
      <Route
        exact
        path={match.path}
      >
        <EligibilityCheck
          historyPush={history.push}
          pathname={location.pathname}
        />
      </Route>
      <Route>
        <NotMatch />
      </Route>
    </Switch>
  )
}

CreateAccount.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    path: PropTypes.string.isRequired,
  }).isRequired,
}

export default CreateAccount
