import React, { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'

import { api } from 'apiClient/api'
import { SAVED_OFFERER_ID_KEY } from 'core/shared/constants'
import { updateFeatures } from 'store/features/reducer'
import { updateSelectedOffererId, updateUser } from 'store/user/reducer'
import Spinner from 'ui-kit/Spinner/Spinner'
import { localStorageAvailable } from 'utils/localStorageAvailable'

import styles from './StoreProvider.module.scss'

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

      if (localStorageAvailable()) {
        const savedOffererId = localStorage.getItem(SAVED_OFFERER_ID_KEY)
        dispatch(
          updateSelectedOffererId(
            savedOffererId ? Number(savedOffererId) : null
          )
        )
      }
      setIsStoreInitialized(true)
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getStoreInitialState()
  }, [isAdageIframe, dispatch])

  if (!isStoreInitialized) {
    return (
      <main id="content" className={styles['spinner-container']}>
        <Spinner />
      </main>
    )
  }

  return children
}

export default StoreProvider
