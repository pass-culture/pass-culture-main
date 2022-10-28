import React, { useCallback, useEffect, useState } from 'react'
import {
  Route,
  Switch,
  useHistory,
  useLocation,
  useParams,
  useRouteMatch,
} from 'react-router'

import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { IOfferIndividual } from 'core/Offers/types'
import { useHomePath } from 'hooks'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'
import { parse } from 'utils/query-string'

import getWizardData, {
  IOfferWizardData,
} from './adapters/getWizardData/getWizardData'
import { Confirmation } from './Confirmation'
import { Offer } from './Offer'
import { Stocks } from './Stocks'
import { Summary } from './Summary'

export interface IDataLoading {
  isLoading: true
  error?: undefined
  offer?: IOfferIndividual
}
export interface IDataSuccess extends IOfferWizardData {
  isLoading: false
  error?: undefined
  offer?: IOfferIndividual
}
export interface IDataError {
  isLoading: false
  error: string
  offer?: undefined
}

const OfferIndividualWizard = () => {
  const [data, setData] = useState<IDataLoading | IDataSuccess | IDataError>({
    isLoading: true,
  })
  const homePath = useHomePath()
  const notify = useNotification()
  const history = useHistory()
  const { path } = useRouteMatch()

  const { currentUser } = useCurrentUser()

  const { offerId } = useParams<{ offerId: string }>()
  const { search } = useLocation()
  const { structure: offererId } = parse(search)

  const loadOffer = useCallback(async () => {
    const response = await getOfferIndividualAdapter(offerId)
    if (response.isOk) {
      setData({
        offererNames: [],
        venueList: [],
        categoriesData: {
          categories: [],
          subCategories: [],
        },
        isLoading: data.isLoading,
        offer: response.payload,
        error: undefined,
      })
      return Promise.resolve(response.payload)
    }
    notify.error(response.message, { withStickyActionBar: true })
    history.push(homePath)
    return Promise.resolve()
  }, [offerId])
  useEffect(() => {
    offerId && loadOffer()
  }, [offerId])

  useEffect(() => {
    async function loadData() {
      const response = await getWizardData({
        offer: data.offer,
        queryOffererId: offererId,
        isAdmin: currentUser.isAdmin,
      })
      if (response.isOk) {
        setData({ isLoading: false, offer: data.offer, ...response.payload })
      } else {
        setData({
          isLoading: false,
          error: response.message,
        })
      }
    }
    ;(!offerId || data.offer) && loadData()
  }, [offerId, data.offer])

  if (data.isLoading === true) return <Spinner />
  if (data.error !== undefined) {
    notify.error(data.error, { withStickyActionBar: true })
    history.push(homePath)
    return null
  }

  const contextValues: IOfferIndividualContext = {
    offerId: offerId || null,
    offer: data.offer || null,
    venueList: data.venueList,
    offererNames: data.offererNames,
    categories: data.categoriesData.categories,
    subCategories: data.categoriesData.subCategories,
    reloadOffer: () => loadOffer(),
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
