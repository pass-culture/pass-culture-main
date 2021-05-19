import PropTypes from 'prop-types'
import React from 'react'
import { Route, Switch } from 'react-router-dom'

import NotFound from 'components/pages/Errors/NotFound/NotFound'
import OffererCreationContainer from 'components/pages/Offerer/OffererCreation/OffererCreationContainer'
import OffererDetailsLayout from 'components/pages/Offerers/OffererDetails/OffererDetailsLayout'

import OfferersContainer from './List/OfferersContainer'

const OfferersLayout = ({ match }) => {
  return (
    <Switch>
      <Route
        exact
        path={match.path}
      >
        <OfferersContainer />
      </Route>
      <Route
        exact
        path={`${match.path}/creation`}
      >
        <OffererCreationContainer />
      </Route>
      <Route path={`${match.path}/:offererId([A-Z0-9]+)`}>
        <OffererDetailsLayout />
      </Route>
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

OfferersLayout.propTypes = {
  match: PropTypes.shape({
    path: PropTypes.string.isRequired,
  }).isRequired,
}

export default OfferersLayout
