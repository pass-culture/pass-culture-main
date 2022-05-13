import Breadcrumb, { STEP_ID_INFORMATIONS, mapPathToStep } from '../Breadcrumb'
import {
  Redirect,
  Route,
  Switch,
  useParams,
  useRouteMatch,
} from 'react-router-dom'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import PropTypes from 'prop-types'
import React from 'react'
import Titles from 'components/layout/Titles/Titles'

const VenueCreation = ({ isTemporary }) => {
  let { offererId, venueId } = useParams()

  const match = useRouteMatch()
  const pageTitle = isTemporary ? 'Créer un lieu temporaire' : 'Créer un lieu'

  const stepName = location.pathname.match(/[a-z]+$/)
  const activeStep = stepName
    ? mapPathToStep[stepName[0]]
    : STEP_ID_INFORMATIONS

  return (
    <div>
      <PageTitle title={pageTitle} />
      <Titles title={pageTitle} />

      <Breadcrumb
        activeStep={activeStep}
        offererId={offererId}
        venueId={venueId}
      />

      <Switch>
        <Route exact path={`${match.path}/informations`}>
          <p>
            {isTemporary
              ? 'create temporary venue information form'
              : 'create venue information form'}
          </p>
        </Route>
        <Route exact path={`${match.path}/gestion`}>
          <p>create venue management form</p>
        </Route>
        <Route exact path={match.path}>
          <Redirect to={`${match.url}/informations`} />
        </Route>
      </Switch>
    </div>
  )
}

VenueCreation.defaultProps = {
  isTemporary: false,
}

VenueCreation.propTypes = {
  isTemporary: PropTypes.bool,
}

export default VenueCreation
