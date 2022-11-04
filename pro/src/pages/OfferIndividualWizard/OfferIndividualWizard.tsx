import React from 'react'
import {
  Route,
  Switch,
  useLocation,
  useParams,
  useRouteMatch,
} from 'react-router'

import { OfferIndividualContextProvider } from 'context/OfferIndividualContext'
import useCurrentUser from 'hooks/useCurrentUser'
import { parse } from 'utils/query-string'

import { Confirmation } from './Confirmation'
import { Offer } from './Offer'
import { Stocks } from './Stocks'
import { Summary } from './Summary'

const OfferIndividualWizard = () => {
  const { path } = useRouteMatch()
  const { currentUser } = useCurrentUser()
  const { offerId } = useParams<{ offerId: string }>()
  const { search } = useLocation()
  const { structure: offererId } = parse(search)

  return (
    <OfferIndividualContextProvider
      isUserAdmin={currentUser.isAdmin}
      offerId={offerId}
      queryOffererId={offererId}
    >
      <Switch>
        <Route
          exact
          path={[
            `${path}/creation/individuelle/informations`,
            `${path}/brouillon/individuelle/informations`,
            `${path}/individuelle/informations`,
          ]}
        >
          <Offer />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/individuelle/stocks`,
            `${path}/brouillon/individuelle/stocks`,
            `${path}/individuelle/stocks`,
          ]}
        >
          <Stocks />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/individuelle/recapitulatif`,
            `${path}/brouillon/individuelle/recapitulatif`,
            `${path}/individuelle/recapitulatif`,
          ]}
        >
          <Summary />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/individuelle/confirmation`,
            `${path}/brouillon/individuelle/confirmation`,
            `${path}/individuelle/confirmation`,
          ]}
        >
          <Confirmation />
        </Route>
      </Switch>
    </OfferIndividualContextProvider>
  )
}

export default OfferIndividualWizard
