import { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'

import { api } from '@/apiClient/api'
import { SAVED_OFFERER_ID_KEY } from '@/commons/core/shared/constants'
import { updateFeatures } from '@/commons/store/features/reducer'
import {
  updateCurrentOfferer,
  updateOffererNames,
} from '@/commons/store/offerer/reducer'
import { updateUser, updateUserAccess } from '@/commons/store/user/reducer'
import { storageAvailable } from '@/commons/utils/storageAvailable'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

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

    const initializeUserOfferer = async () => {
      if (isAdageIframe) {
        return
      }
      try {
        const response = await api.listOfferersNames()
        const firstOffererId = response.offerersNames[0]?.id

        let offererIdToUse = firstOffererId
        if (storageAvailable('localStorage')) {
          const savedOffererId = localStorage.getItem(SAVED_OFFERER_ID_KEY)
          offererIdToUse = savedOffererId
            ? Number(savedOffererId)
            : firstOffererId
        }

        try {
          const offererObj = offererIdToUse
            ? await api.getOfferer(offererIdToUse)
            : null
          dispatch(updateCurrentOfferer(offererObj))

          dispatch(
            updateUserAccess(
              response.offerersNames.length > 0
                ? offererObj?.isOnboarded
                  ? 'full'
                  : 'no-onboarding'
                : 'no-offerer'
            )
          )
        } catch {
          if (response.offerersNames.length > 0) {
            dispatch(updateUserAccess('unattached'))
          } else {
            dispatch(updateUserAccess('no-offerer'))
          }
        } finally {
          dispatch(updateOffererNames(response.offerersNames))
        }
      } catch {
        // In any other case, it's a normal error
        dispatch(updateCurrentOfferer(null))
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
      <main id={'content'} className={styles['spinner-container']}>
        <Spinner />
      </main>
    )
  }

  return children
}
