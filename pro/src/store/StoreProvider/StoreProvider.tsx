import React, { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'

import { api } from 'apiClient/api'
import { updateFeatures } from 'store/features/reducer'
import { updateUser } from 'store/user/reducer'
import Spinner from 'ui-kit/Spinner/Spinner'

interface StoreProviderProps {
  children: JSX.Element | JSX.Element[]
  isAdageIframe?: boolean
}

const StoreProvider = ({
  children,
  isAdageIframe = false,
}: StoreProviderProps) => {
  const dispatch = useDispatch()
  const [isStoreInitialized, setIsStoreInitialized] = useState(false)

  useEffect(() => {
    const initializeUser = async () => {
      if (isAdageIframe) {
        return
      }
      try {
        const response = await api.getProfile()
        dispatch(updateUser(response))
      } catch {
        dispatch(updateUser(null))
      }
    }

    const initializeFeatures = async () => {
      try {
        const response = await api.listFeatures()
        dispatch(updateFeatures(response))
      } catch {
        dispatch(updateFeatures([]))
      }
    }

    const getStoreInitialState = async () => {
      await Promise.all([initializeUser(), initializeFeatures()])
      setIsStoreInitialized(true)
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getStoreInitialState()
  }, [isAdageIframe, dispatch])

  if (!isStoreInitialized) {
    return (
      <main id="content" className="spinner-container">
        <Spinner />
      </main>
    )
  }

  return children
}

export default StoreProvider
