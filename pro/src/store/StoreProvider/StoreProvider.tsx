import React, { useEffect, useState } from 'react'
import { Provider } from 'react-redux'

import { api } from 'apiClient/api'
import {
  FeatureResponseModel,
  GetOffererNameResponseModel,
  SharedCurrentUserResponseModel,
} from 'apiClient/v1'
import createStore from 'store'
import { RootState } from 'store/reducers'
import Spinner from 'ui-kit/Spinner/Spinner'

interface IStoreProvider {
  isDev?: boolean
  children: JSX.Element | JSX.Element[]
}

const StoreProvider = ({ children, isDev = false }: IStoreProvider) => {
  const [currentUser, setCurrentUser] =
    useState<SharedCurrentUserResponseModel | null>()
  const [features, setFeatures] = useState<FeatureResponseModel[]>()
  const [offerersNames, setOfferersNames] =
    useState<Array<GetOffererNameResponseModel> | null>()
  const [initialState, setInitialState] =
    useState<Partial<RootState | null>>(null)

  useEffect(() => {
    function setEmptyInitialData() {
      setCurrentUser(null)
      setFeatures([])
      setOfferersNames([])
    }

    async function getStoreInitialData() {
      api
        .getProfile()
        .then(response => setCurrentUser(response))
        .catch(() => setCurrentUser(null))
      api
        .listFeatures()
        .then(response => setFeatures(response))
        .catch(() => setFeatures([]))
      api
        .listOfferersNames()
        .then(response =>
          setOfferersNames(response ? response.offerersNames : null)
        )
        .catch(() => setOfferersNames(null))
    }
    isDev ? setEmptyInitialData() : getStoreInitialData()
  }, [])

  useEffect(() => {
    if (
      currentUser !== undefined &&
      features !== undefined &&
      offerersNames !== undefined
    ) {
      setInitialState({
        user: { currentUser, initialized: true },
        features: { list: features || [], initialized: true },
        offerersNames: offerersNames || [],
      })
    }
  }, [currentUser, features, offerersNames])

  if (initialState === null)
    return (
      <main className="spinner-container">
        <Spinner />
      </main>
    )

  const { store } = createStore(initialState)
  return <Provider store={store}>{children}</Provider>
}

export default StoreProvider
