import React, { useEffect, useState } from 'react'
import { Provider } from 'react-redux'

import { api } from 'apiClient/api'
import {
  FeatureResponseModel,
  SharedCurrentUserResponseModel,
} from 'apiClient/v1'
import createStore from 'store'
import { RootState } from 'store/reducers'
import Spinner from 'ui-kit/Spinner/Spinner'

interface StoreProviderProps {
  isDev?: boolean
  children: JSX.Element | JSX.Element[]
}

const StoreProvider = ({ children, isDev = false }: StoreProviderProps) => {
  const [currentUser, setCurrentUser] =
    useState<SharedCurrentUserResponseModel | null>()
  const [features, setFeatures] = useState<FeatureResponseModel[]>()
  const [initialState, setInitialState] =
    useState<Partial<RootState | null>>(null)

  useEffect(() => {
    function setEmptyInitialData() {
      setCurrentUser(null)
      setFeatures([])
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
    }
    isDev ? setEmptyInitialData() : getStoreInitialData()
  }, [])

  useEffect(() => {
    if (currentUser !== undefined && features !== undefined) {
      setInitialState({
        user: { currentUser, initialized: true },
        features: { list: features || [], initialized: true },
      })
    }
  }, [currentUser, features])

  if (initialState === null) {
    return (
      <main id="content" className="spinner-container">
        <Spinner />
      </main>
    )
  }

  const { store } = createStore(initialState)
  return <Provider store={store}>{children}</Provider>
}

export default StoreProvider
