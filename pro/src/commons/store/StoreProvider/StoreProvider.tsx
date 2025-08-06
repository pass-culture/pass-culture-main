import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'

import { api } from '@/apiClient//api'
import { SAVED_OFFERER_ID_KEY } from '@/commons/core/shared/constants'
import { updateFeatures } from '@/commons/store/features/reducer'
import {
  updateCurrentOfferer,
  updateOffererNames,
} from '@/commons/store/offerer/reducer'
import { selectCurrentOfferer } from '@/commons/store/offerer/selectors'
import { updateUser } from '@/commons/store/user/reducer'
import { getOffererData } from '@/commons/utils/offererStoreHelper'
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
  const currentOfferer = useSelector(selectCurrentOfferer)

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
        const firstOffererId = response.offerersNames[0].id

        let offererIdToUse = firstOffererId
        if (storageAvailable('localStorage')) {
          const savedOffererId = localStorage.getItem(SAVED_OFFERER_ID_KEY)
          offererIdToUse = savedOffererId
            ? Number(savedOffererId)
            : firstOffererId
        }

        try {
          const offererObj = await getOffererData(
            offererIdToUse,
            currentOfferer,
            () => api.getOfferer(offererIdToUse)
          )
          dispatch(updateCurrentOfferer(offererObj))
          dispatch(updateOffererNames(response.offerersNames))
        } catch {
          dispatch(
            // TODO: Find a better way with the Product team to handle this behavior
            // @ts-expect-error: This is because updateCurrentOfferer() expects its argument to be a full offerer object (which we can't have here because the API will returns a 404 for an offerer awaiting rattachment)
            updateCurrentOfferer({
              id: offererIdToUse,
            })
          )
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
      <main id="content" className={styles['spinner-container']}>
        <Spinner />
      </main>
    )
  }

  return children
}
