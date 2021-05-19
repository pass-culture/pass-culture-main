import PropTypes from 'prop-types'
import React from 'react'
import { Route, Switch } from 'react-router-dom'

import NotFound from 'components/pages/Errors/NotFound/NotFound'

import OfferersContainer from './List/OfferersContainer'
import OffererDetailsLayout from './Offerer/OffererDetailsLayout'
import OffererCreationContainer from './OffererCreation/OffererCreationContainer'

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
