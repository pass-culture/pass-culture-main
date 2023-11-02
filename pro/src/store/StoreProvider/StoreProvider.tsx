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
  isAdageIframe?: boolean
  children: JSX.Element | JSX.Element[]
}

const StoreProvider = ({
  children,
  isAdageIframe = false,
  isDev = false,
}: StoreProviderProps) => {
  const [currentUser, setCurrentUser] =
    useState<SharedCurrentUserResponseModel | null>()
  const [features, setFeatures] = useState<FeatureResponseModel[]>([])
  const [initialState, setInitialState] = useState<Partial<RootState>>()

  useEffect(() => {
    async function getStoreInitialData() {
      if (isAdageIframe) {
        setCurrentUser(null)
      } else {
        await api
          .getProfile()
          .then((response) => setCurrentUser(response))
          .catch(() => setCurrentUser(null))
      }
      await api
        .listFeatures()
        .then((response) => setFeatures(response))
        .catch(() => setFeatures([]))
    }

    if (!isDev) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      getStoreInitialData()
    }
  }, [])

  useEffect(() => {
    if (currentUser !== undefined && features !== undefined) {
      setInitialState({
        user: { currentUser, initialized: true },
        features: { list: features || [], initialized: true },
      })
    }
  }, [currentUser, features])

  const { store } = createStore(initialState)
  return (
    <Provider store={store}>
      <Spinner isLoading={!initialState} />
      {initialState && children}
    </Provider>
  )
}

export default StoreProvider
