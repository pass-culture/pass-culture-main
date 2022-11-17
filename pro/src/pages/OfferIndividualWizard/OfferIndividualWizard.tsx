import React from 'react'
import {
  Route,
  Switch,
  useLocation,
  useParams,
  useRouteMatch,
} from 'react-router'

import { LogRouteNavigation } from 'app/AppRouter/LogRouteNavigation'
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
          path={`${path}/creation/individuelle/informations`}
          render={() => (
            <LogRouteNavigation
              route={{ title: "Offre étape par étape - création d'offre" }}
            >
              <Offer />
            </LogRouteNavigation>
          )}
        />
        <Route
          exact
          path={`${path}/brouillon/individuelle/informations`}
          render={() => (
            <LogRouteNavigation
              route={{ title: "Offre étape par étape - complétion d'offre" }}
            >
              <Offer />
            </LogRouteNavigation>
          )}
        />
        <Route
          exact
          path={`${path}/individuelle/informations`}
          render={() => (
            <LogRouteNavigation
              route={{ title: "Offre étape par étape - édition d'offre" }}
            >
              <Offer />
            </LogRouteNavigation>
          )}
        />
        <Route
          exact
          path={`${path}/creation/individuelle/stocks`}
          render={() => (
            <LogRouteNavigation
              route={{ title: 'Offre étape par étape - création de stocks' }}
            >
              <Stocks />
            </LogRouteNavigation>
          )}
        />
        <Route
          exact
          path={`${path}/brouillon/individuelle/stocks`}
          render={() => (
            <LogRouteNavigation
              route={{ title: 'Offre étape par étape - complétion de stocks' }}
            >
              <Stocks />
            </LogRouteNavigation>
          )}
        />
        <Route
          exact
          path={`${path}/individuelle/stocks`}
          render={() => (
            <LogRouteNavigation
              route={{ title: 'Offre étape par étape - édition de stocks' }}
            >
              <Stocks />
            </LogRouteNavigation>
          )}
        />
        <Route
          exact
          path={`${path}/creation/individuelle/recapitulatif`}
          render={() => (
            <LogRouteNavigation
              route={{
                title:
                  'Offre étape par étape - récapitulatif de création d’offre',
              }}
            >
              <Summary />
            </LogRouteNavigation>
          )}
        />
        <Route
          exact
          path={`${path}/brouillon/individuelle/recapitulatif`}
          render={() => (
            <LogRouteNavigation
              route={{
                title:
                  'Offre étape par étape - récapitulatif de complétion d’offre',
              }}
            >
              <Summary />
            </LogRouteNavigation>
          )}
        />
        <Route
          exact
          path={`${path}/individuelle/recapitulatif`}
          render={() => (
            <LogRouteNavigation
              route={{ title: 'Offre étape par étape - récapitulatif' }}
            >
              <Summary />
            </LogRouteNavigation>
          )}
        />

        <Route
          exact
          path={[
            `${path}/creation/individuelle/confirmation`,
            `${path}/brouillon/individuelle/confirmation`,
            `${path}/individuelle/confirmation`,
          ]}
          render={() => (
            <LogRouteNavigation
              route={{ title: 'Offre étape par étape - confirmation' }}
            >
              <Confirmation />
            </LogRouteNavigation>
          )}
        />
        <Route
          exact
          path={`${path}/brouillon/individuelle/confirmation`}
          render={() => (
            <LogRouteNavigation
              route={{
                title:
                  'Offre étape par étape - confirmation de publication de votre brouillon',
              }}
            >
              <Confirmation />
            </LogRouteNavigation>
          )}
        />
        <Route
          exact
          path={`${path}/creation/individuelle/confirmation`}
          render={() => (
            <LogRouteNavigation
              route={{ title: 'Offre étape par étape - confirmation' }}
            >
              <Confirmation />
            </LogRouteNavigation>
          )}
        />
      </Switch>
    </OfferIndividualContextProvider>
  )
}

export default OfferIndividualWizard
