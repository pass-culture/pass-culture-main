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
import { useContext, useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import { api } from 'apiClient/api'
import { firebaseConfig } from 'config/firebase'
import { AnalyticsContext } from 'context/analyticsContext'
import useUtmQueryParams from 'hooks/useUtmQueryParams'
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

export const useFirebase = (consentedToFirebase: boolean) => {
  const currentUser = useSelector(selectCurrentUser)
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const [isFirebaseInitialized, setIsFirebaseInitialized] =
    useState<boolean>(false)

  const { setLogEvent } = useAnalytics()
  const utmParameters = useUtmQueryParams()

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

      const remoteConfigParams = getRemoteConfigParams()
      await api.postProFlags({
        firebase: { ...remoteConfigParams, REMOTE_CONFIG_LOADED: 'true' },
      })

      setLogEvent &&
        setLogEvent(
          () =>
            (
              event: string,
              params:
                | { [key: string]: string | boolean | string[] | undefined }
                | Record<string, never> = {}
            ) => {
              if (!firebaseRemoteConfig) {
                return
              }
              const remoteConfigParams = getRemoteConfigParams()
              analyticsLogEvent(getAnalytics(firebaseApp), event, {
                ...params,
                ...utmParameters,
                ...remoteConfigParams,
              })
            }
        )
    }

    if (consentedToFirebase && !firebaseApp) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      loadAnalytics()
    }
  }, [consentedToFirebase])

  useEffect(() => {
    if (consentedToFirebase && firebaseApp && currentUser) {
      setUserId(getAnalytics(firebaseApp), currentUser.id.toString())
    }
  }, [consentedToFirebase, currentUser, isFirebaseInitialized])

  useEffect(() => {
    if (firebaseApp && selectedOffererId) {
      setUserProperties(getAnalytics(firebaseApp), {
        offerer_id: selectedOffererId.toString(),
      })
    }
  }, [selectedOffererId, isFirebaseInitialized])
}

function useAnalytics() {
  return useContext(AnalyticsContext)
}

export default useAnalytics
