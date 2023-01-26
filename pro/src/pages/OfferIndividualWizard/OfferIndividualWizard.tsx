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
          <PageTitle title="Détails de l'offre" />
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
          <PageTitle title="Détails de l'offre" />
          <Offer />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/tarifs`,
            `${path}/brouillon/tarifs`,
            `${path}/tarifs`,
          ]}
        >
          <PageTitle title="Vos tarifs" />
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
          <PageTitle title="Vos stocks" />
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
          <PageTitle title="Récapitulatif" />
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
          <PageTitle title="Confirmation" />
          <Confirmation />
        </Route>
      </Switch>
    </OfferIndividualContextProvider>
  )
}

export default OfferIndividualWizard
