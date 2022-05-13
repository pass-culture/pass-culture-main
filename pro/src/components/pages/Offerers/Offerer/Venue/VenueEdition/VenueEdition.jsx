import Breadcrumb, { STEP_ID_INFORMATIONS, mapPathToStep } from '../Breadcrumb'
import {
  Redirect,
  Route,
  Switch,
  useParams,
  useRouteMatch,
} from 'react-router-dom'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import React from 'react'
import Titles from 'components/layout/Titles/Titles'

const VenueEdition = () => {
  let { offererId, venueId } = useParams()

  const match = useRouteMatch()

  const stepName = location.pathname.match(/[a-z]+$/)
  const activeStep = stepName
    ? mapPathToStep[stepName[0]]
    : STEP_ID_INFORMATIONS

  return (
    <div>
      <PageTitle title="Détails de votre lieu" />
      <Titles title="Editer votre lieu" />

      <Breadcrumb
        activeStep={activeStep}
        offererId={offererId}
        venueId={venueId}
      />

      <Switch>
        <Route path={`${match.path}/informations`}>
          <p>edit venue information form</p>
        </Route>
        <Route path={`${match.path}/gestion`}>
          <p>edit venue management form</p>
        </Route>

        <Route exact path={match.path}>
          <Redirect to={`${match.url}/informations`} />
        </Route>
      </Switch>
    </div>
  )
}

export default VenueEdition
