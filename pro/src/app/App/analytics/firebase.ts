/* istanbul ignore file: DEBT, TO FIX */
import {
  getAnalytics,
  initializeAnalytics,
  isSupported,
  logEvent as analyticsLogEvent,
  setUserId,
  setUserProperties,
} from '@firebase/analytics'
import * as firebase from '@firebase/app'
import {
  RemoteConfig,
  fetchAndActivate,
  getAll,
  getRemoteConfig,
} from '@firebase/remote-config'
import { useCallback, useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import { firebaseConfig } from 'config/firebase'
import { useUtmQueryParams } from 'hooks/useUtmQueryParams'
import { selectCurrentOffererId, selectCurrentUser } from 'store/user/selectors'

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
  const currentUser = useSelector(selectCurrentUser)
  const selectedOffererId = useSelector(selectCurrentOffererId)
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

      initializeAnalytics(firebaseApp, { config: { send_page_view: false } })
      firebaseRemoteConfig = getRemoteConfig(firebaseApp)
      await fetchAndActivate(firebaseRemoteConfig)
    }

    if (consentedToFirebase) {
      if (!firebaseApp) {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        loadAnalytics()
      }
    } else {
      if (firebaseApp) {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
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
    if (isFirebaseInitialized && selectedOffererId) {
      setUserProperties(getAnalytics(firebaseApp), {
        offerer_id: selectedOffererId.toString(),
      })
    }
  }, [selectedOffererId, isFirebaseInitialized])
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
  return remoteConfigParams
}

export const useAnalytics = () => {
  const utmParameters = useUtmQueryParams()

  const logEvent = useCallback(
    (
      event: string,
      params?: {
        [key: string]: string | string[] | number | boolean | undefined
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
