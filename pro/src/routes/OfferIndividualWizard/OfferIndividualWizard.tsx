import React from 'react'
import {
  Route,
  Switch,
  useHistory,
  useParams,
  useRouteMatch,
} from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { useHomePath } from 'hooks'

import { Confirmation } from './Confirmation'
import { useGetData } from './hooks'
import { Offer } from './Offer'
import { Stocks } from './Stocks'
import { Summary } from './Summary'

const OfferIndividualWizard = () => {
  const homePath = useHomePath()
  const notify = useNotification()
  const history = useHistory()
  const { path } = useRouteMatch()

  const { offerId } = useParams<{ offerId: string }>()
  const { data, isLoading, loadingError, reloadOffer } = useGetData(offerId)

  if (isLoading === true) return <Spinner />
  if (loadingError !== undefined) {
    notify.error(loadingError)
    history.push(homePath)
    return null
  }

  const {
    offer,
    venueList,
    offererNames,
    categoriesData: { categories, subCategories },
  } = data

  const contextValues: IOfferIndividualContext = {
    offerId: offerId || null,
    offer: offer || null,
    venueList,
    offererNames,
    categories,
    subCategories,
    reloadOffer,
  }

  return (
    <OfferIndividualContext.Provider value={contextValues}>
      <Switch>
        <Route
          exact
          path={[
            `${path}/creation/individuelle/informations`,
            `${path}/individuelle/informations`,
          ]}
        >
          <Offer />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/individuelle/stocks`,
            `${path}/individuelle/stocks`,
          ]}
        >
          <Stocks />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/individuelle/recapitulatif`,
            `${path}/individuelle/recapitulatif`,
          ]}
        >
          <Summary />
        </Route>
        <Route
          exact
          path={[
            `${path}/creation/individuelle/confirmation`,
            `${path}/individuelle/confirmation`,
          ]}
        >
          <Confirmation />
        </Route>
      </Switch>
    </OfferIndividualContext.Provider>
  )
}

export default OfferIndividualWizard
