import { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'

import { api } from '@/apiClient/api'
import { updateFeatures } from '@/commons/store/features/reducer'
import { updateUser } from '@/commons/store/user/reducer'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import type { AppDispatch } from '../store'
import { initializeUser } from '../user/dispatchers/initializeUser'
import styles from './StoreProvider.module.scss'

interface StoreProviderProps {
  children: JSX.Element | JSX.Element[]
  isAdageIframe?: boolean
}

export const StoreProvider = ({
  children,
  isAdageIframe = false,
}: StoreProviderProps) => {
  const dispatch = useDispatch<AppDispatch>()
  const [isStoreInitialized, setIsStoreInitialized] = useState(false)

  useEffect(() => {
    const getUser = async () => {
      try {
        return await api.getProfile()
      } catch {
        return null
      }
    }

    const getFeatures = async () => {
      try {
        return await api.listFeatures()
      } catch {
        return []
      }
    }

    const getStoreInitialState = async () => {
      const features = await getFeatures()
      dispatch(updateFeatures(features))

      if (!isAdageIframe) {
        const user = await getUser()
        dispatch(updateUser(user))
        if (user) {
          await dispatch(initializeUser(user)).unwrap()
        }
      }

      setIsStoreInitialized(true)
    }

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
