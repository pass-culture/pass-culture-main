import { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'

import { api } from 'apiClient/api'
import { HTTP_STATUS, isErrorAPIError } from 'apiClient/helpers'
import { SAVED_OFFERER_ID_KEY } from 'commons/core/shared/constants'
import { updateFeatures } from 'commons/store/features/reducer'
import {
  updateOffererNames,
  updateSelectedOffererId,
  updateOffererIsOnboarded,
} from 'commons/store/offerer/reducer'
import { updateUser } from 'commons/store/user/reducer'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './StoreProvider.module.scss'

interface StoreProviderProps {
  children: JSX.Element | JSX.Element[]
  isAdageIframe?: boolean
}

export const StoreProvider = ({
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

    const inisializeOffererIsOnboarded = async (offererId: number) => {
      try {
        const response = await api.getOfferer(offererId)
        dispatch(updateOffererIsOnboarded(response.isOnboarded))
      } catch (e) {
        // 403 for this call means the user is not yet linked to the offerer.
        updateOffererIsOnboarded(
          isErrorAPIError(e) && e.status === HTTP_STATUS.FORBIDDEN
        )
      }
    }

    const initializeUserOfferer = async () => {
      if (isAdageIframe) {
        return
      }
      try {
        const response = await api.listOfferersNames()
        const firstOffererId = response.offerersNames[0].id

        if (storageAvailable('localStorage')) {
          const savedOffererId = localStorage.getItem(SAVED_OFFERER_ID_KEY)
          dispatch(
            updateSelectedOffererId(
              savedOffererId ? Number(savedOffererId) : firstOffererId
            )
          )
          await inisializeOffererIsOnboarded(
            savedOffererId ? Number(savedOffererId) : firstOffererId
          )
        } else {
          dispatch(updateSelectedOffererId(firstOffererId))
          await inisializeOffererIsOnboarded(firstOffererId)
        }
        dispatch(updateOffererNames(response.offerersNames))
      } catch {
        dispatch(updateSelectedOffererId(null))
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
      await Promise.all([
        initializeUser(),
        initializeFeatures(),
        initializeUserOfferer(),
      ])
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
