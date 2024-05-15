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
  fetchAndActivate,
  getAll,
  getRemoteConfig,
} from '@firebase/remote-config'
import { useContext, useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import { firebaseConfig } from 'config/firebase'
import { AnalyticsContext } from 'context/analyticsContext'
import useUtmQueryParams from 'hooks/useUtmQueryParams'
import { selectCurrentOffererId, selectCurrentUser } from 'store/user/selectors'

import useRemoteConfig from '../../../hooks/useRemoteConfig'

let firebaseApp: firebase.FirebaseApp | undefined

export const useFirebase = (consentedToFirebase: boolean) => {
  const currentUser = useSelector(selectCurrentUser)

  const [isFirebaseInitialized, setIsFirebaseInitialized] =
    useState<boolean>(false)
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const { setLogEvent } = useAnalytics()
  const { setRemoteConfig, setRemoteConfigData } = useRemoteConfig()
  const utmParameters = useUtmQueryParams()

  useEffect(() => {
    const loadAnalytics = async () => {
      const isFirebaseSupported = await isSupported()
      if (!isFirebaseSupported) {
        return
      }

      firebaseApp = firebase.initializeApp(firebaseConfig)
      setIsFirebaseInitialized(true)

      initializeAnalytics(firebaseApp, {
        config: { send_page_view: false },
      })
      const remoteConfig = getRemoteConfig(firebaseApp)
      await fetchAndActivate(remoteConfig)
      setRemoteConfig && setRemoteConfig(remoteConfig)
      setLogEvent &&
        setLogEvent(
          () =>
            (
              event: string,
              params:
                | { [key: string]: string | boolean | string[] | undefined }
                | Record<string, never> = {}
            ) => {
              const remoteConfigValues = getAll(remoteConfig)
              const remoteConfigParams: Record<string, string> = {}
              Object.keys(remoteConfigValues).forEach((k) => {
                remoteConfigParams[k] = remoteConfigValues[k].asString()
              })
              setRemoteConfigData &&
                setRemoteConfigData({
                  ...remoteConfigParams,
                  REMOTE_CONFIG_LOADED: 'true',
                })
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
