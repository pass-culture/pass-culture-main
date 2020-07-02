import React from 'react'
import { Route, Switch } from 'react-router'
import PropTypes from 'prop-types'

import Eligible from './Eligible/Eligible'
import IneligibleDepartment from './IneligibleDepartment/IneligibleDepartment'
import IneligibleOverEighteen from './IneligibleOverEighteen/IneligibleOverEighteen'
import EligibleSoon from './EligibleSoon/EligibleSoon'
import IneligibleUnderEighteen from './IneligibleUnderEighteen/IneligibleUnderEighteen'
import ContactSaved from './ContactSaved/ContactSaved'
import EligibilityCheck from './EligibilityCheck/EligibilityCheck'

const CreateAccount = ({ history, location }) => (
  <Switch>
    <Route path="/verification-eligibilite/eligible">
      <Eligible />
    </Route>
    <Route path="/verification-eligibilite/departement-non-eligible">
      <IneligibleDepartment />
    </Route>
    <Route path="/verification-eligibilite/pas-eligible">
      <IneligibleOverEighteen />
    </Route>
    <Route path="/verification-eligibilite/bientot">
      <EligibleSoon />
    </Route>
    <Route path="/verification-eligibilite/trop-tot">
      <IneligibleUnderEighteen />
    </Route>
    <Route path="/verification-eligibilite/gardons-contact">
      <ContactSaved />
    </Route>
    <Route path="/verification-eligibilite">
      <EligibilityCheck
        historyPush={history.push}
        pathname={location.pathname}
      />
    </Route>
  </Switch>
)

CreateAccount.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }).isRequired,

}

export default CreateAccount
