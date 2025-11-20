import { useEffect, useState } from 'react'

import { api } from '@/apiClient/api'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { updateFeatures } from '@/commons/store/features/reducer'
import { updateUser } from '@/commons/store/user/reducer'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

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
  const dispatch = useAppDispatch()
  const [isStoreInitialized, setIsStoreInitialized] = useState(false)

  useEffect(() => {
    const getUser = async () => {
      return await api.getProfile()
      console.log('error')
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
        console.log('??')
        const user = await getUser()
        console.log({ user })
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
