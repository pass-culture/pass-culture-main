import {
  logEvent as analyticsLogEvent,
  getAnalytics,
  initializeAnalytics,
  isSupported,
  setUserId,
  setUserProperties,
} from '@firebase/analytics'
import * as firebase from '@firebase/app'
import {
  fetchAndActivate,
  getAll,
  getRemoteConfig,
  type RemoteConfig,
} from '@firebase/remote-config'
import { useCallback, useEffect, useState } from 'react'

import { isError } from '@/apiClient/helpers'
import { firebaseConfig } from '@/commons/config/firebase'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useUtmQueryParams } from '@/commons/hooks/useUtmQueryParams'
import { selectCurrentUser } from '@/commons/store/user/selectors'

let firebaseApp: firebase.FirebaseApp | undefined
let firebaseRemoteConfig: RemoteConfig | undefined

const getRemoteConfigParams = (): Record<string, string> => {
  if (!firebaseRemoteConfig) {
    return {}
  }

  const remoteConfigValues = getAll(firebaseRemoteConfig)
  const remoteConfigParams: Record<string, string> = {}
  Object.keys(remoteConfigValues).forEach((k) => {
    remoteConfigParams[k] = remoteConfigValues[k].asString()
  })

  return remoteConfigParams
}

export const destroyFirebase = async () => {
  if (firebaseApp) {
    await firebase.deleteApp(firebaseApp)
    firebaseApp = undefined
    firebaseRemoteConfig = undefined
  }
}

export const useFirebase = (consentedToFirebase: boolean) => {
  const currentUser = useAppSelector(selectCurrentUser)
  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )
  const [isFirebaseInitialized, setIsFirebaseInitialized] =
    useState<boolean>(false)

  useEffect(() => {
    const loadAnalytics = async () => {
      const isFirebaseSupported = await isSupported()
      if (!isFirebaseSupported) {
        return
      }

      firebaseApp = firebase.initializeApp(firebaseConfig)
      setIsFirebaseInitialized(true)

      try {
        initializeAnalytics(firebaseApp, { config: { send_page_view: false } })
        firebaseRemoteConfig = getRemoteConfig(firebaseApp)
        await fetchAndActivate(firebaseRemoteConfig)
      } catch (err) {
        // Throws in any error case that is NOT an "InvalidStateError" (Failed to execute 'transaction' on 'IDBDatabase': The database connection is closing (https://pass-culture.sentry.io/issues/37336598))
        if (!isError(err) || err.name !== 'InvalidStateError') {
          throw err
        }
      }
    }

    if (consentedToFirebase) {
      if (!firebaseApp) {
        loadAnalytics()
      }
    } else {
      if (firebaseApp) {
        destroyFirebase()
        setIsFirebaseInitialized(false)
      }
    }
  }, [consentedToFirebase])

  useEffect(() => {
    if (isFirebaseInitialized && currentUser) {
      setUserId(getAnalytics(firebaseApp), currentUser.id.toString())
    }
  }, [currentUser, isFirebaseInitialized])

  useEffect(() => {
    if (isFirebaseInitialized && selectedPartnerVenue) {
      setUserProperties(getAnalytics(firebaseApp), {
        offerer_id: selectedPartnerVenue.managingOfferer.id.toString(),
      })
    }
  }, [selectedPartnerVenue, isFirebaseInitialized])
}

export const useRemoteConfigParams = () => {
  const [remoteConfigParams, setRemoteConfigParams] = useState<
    Record<string, string>
  >({})

  useEffect(() => {
    const intervalId = setInterval(() => {
      if (firebaseRemoteConfig) {
        clearInterval(intervalId)
        setRemoteConfigParams(getRemoteConfigParams())
      }
    }, 1000)

    return () => clearInterval(intervalId)
  }, [])

  if (firebaseRemoteConfig) {
    return getRemoteConfigParams()
  }

  return remoteConfigParams
}

export const useAnalytics = () => {
  const utmParameters = useUtmQueryParams()

  const logEvent = useCallback(
    (
      event: string,
      params?: {
        [key: string]:
          | string
          | string[]
          | number
          | boolean
          | undefined
          // biome-ignore lint/suspicious/noExplicitAny: Generic params type.
          | Record<string, any>
      }
    ) => {
      if (!firebaseApp || !firebaseRemoteConfig) {
        return
      }

      const remoteConfigParams = getRemoteConfigParams()
      analyticsLogEvent(getAnalytics(firebaseApp), event, {
        ...params,
        ...utmParameters,
        ...remoteConfigParams,
      })
    },
    [utmParameters]
  )

  return { logEvent }
}
