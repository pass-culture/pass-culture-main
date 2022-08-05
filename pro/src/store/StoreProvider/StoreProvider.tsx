import React, { useEffect, useState } from 'react'
import { Provider } from 'react-redux'

import { api } from 'apiClient/api'
import {
  FeatureResponseModel,
  SharedCurrentUserResponseModel,
} from 'apiClient/v1'
import Spinner from 'components/layout/Spinner'
import configureStore from 'store'
import { RootState } from 'store/reducers'

interface IStoreProvider {
  children: JSX.Element | JSX.Element[]
}

const StoreProvider = ({ children }: IStoreProvider) => {
  const [currentUser, setCurrentUser] =
    useState<SharedCurrentUserResponseModel | null>()
  const [features, setFeatures] = useState<FeatureResponseModel[]>()
  const [initialState, setInitialState] =
    useState<Partial<RootState | null>>(null)

  useEffect(() => {
    async function getStoreInitialData() {
      api
        .getProfile()
        .then(response => setCurrentUser(response))
        .catch(() => setCurrentUser(null))
      api
        .listFeatures()
        .then(response => setFeatures(response))
        .catch(() => setFeatures([]))
    }
    getStoreInitialData()
  }, [])

  useEffect(() => {
    if (currentUser !== undefined && features !== undefined) {
      setInitialState({
        user: { currentUser, initialized: true },
        features: { list: features || [], initialized: true },
      })
    }
  }, [currentUser, features])

  if (initialState === null)
    return (
      <main className="spinner-container">
        <Spinner />
      </main>
    )

  const { store } = configureStore(initialState)
  return <Provider store={store}>{children}</Provider>
}

export default StoreProvider
