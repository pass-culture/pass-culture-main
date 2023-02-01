import React from 'react'
import {
  Route,
  Switch,
  useLocation,
  useParams,
  useRouteMatch,
} from 'react-router'

import PageTitle from 'components/PageTitle/PageTitle'
import { OfferIndividualContextProvider } from 'context/OfferIndividualContext'
import useCurrentUser from 'hooks/useCurrentUser'
import { parse } from 'utils/query-string'

import { Confirmation } from './Confirmation'
import { Offer } from './Offer'
import { PriceCategories } from './PriceCategories'
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
      offerId={offerId === 'creation' ? undefined : offerId}
      queryOffererId={offererId}
    >
      <Switch>
        <Route exact path={`/offre/individuelle/creation/informations`}>
          <Offer />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/informations`,
            `${path}/brouillon/informations`,
            `${path}/informations`,
          ]}
        >
          <Offer />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/tarifs`,
            `${path}/brouillon/tarif`,
            `${path}/tarifs`,
          ]}
        >
          <PriceCategories />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/stocks`,
            `${path}/brouillon/stocks`,
            `${path}/stocks`,
          ]}
        >
          <Stocks />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/recapitulatif`,
            `${path}/brouillon/recapitulatif`,
            `${path}/recapitulatif`,
          ]}
        >
          <Summary />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/confirmation`,
            `${path}/brouillon/confirmation`,
            `${path}/confirmation`,
          ]}
        >
          <Confirmation />
        </Route>
      </Switch>
    </OfferIndividualContextProvider>
  )
}

export default OfferIndividualWizard
