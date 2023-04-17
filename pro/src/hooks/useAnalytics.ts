/* istanbul ignore file: DEBT, TO FIX */
import {
  getAnalytics,
  initializeAnalytics,
  isSupported,
  logEvent as analyticsLogEvent,
  setUserId,
} from '@firebase/analytics'
import * as firebase from '@firebase/app'
import {
  fetchAndActivate,
  getAll,
  getRemoteConfig,
} from '@firebase/remote-config'
import { useContext, useEffect, useState } from 'react'

import { firebaseConfig } from 'config/firebase'
import { AnalyticsContext } from 'context/analyticsContext'
import useUtmQueryParams from 'hooks/useUtmQueryParams'

import useRemoteConfig from './useRemoteConfig'

export const useConfigureFirebase = (currentUserId: string | undefined) => {
  const [app, setApp] = useState<firebase.FirebaseApp | undefined>()
  const [isFirebaseSupported, setIsFirebaseSupported] = useState<boolean>(false)

  const { setLogEvent } = useAnalytics()
  const { setRemoteConfig, setRemoteConfigData } = useRemoteConfig()
  const utmParameters = useUtmQueryParams()

  useEffect(() => {
    async function initializeIfNeeded() {
      setIsFirebaseSupported(await isSupported())
    }
    initializeIfNeeded()
  }, [])

  useEffect(() => {
    if (!app && isFirebaseSupported) {
      const initializeApp = firebase.initializeApp(firebaseConfig)
      setApp(initializeApp)
      isFirebaseSupported &&
        initializeAnalytics(initializeApp, {
          config: {
            send_page_view: false,
          },
        })
      const remoteConfig = getRemoteConfig(initializeApp)
      fetchAndActivate(remoteConfig).then(() => {
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
                Object.keys(remoteConfigValues).forEach(k => {
                  remoteConfigParams[k] = remoteConfigValues[k].asString()
                })
                setRemoteConfigData && setRemoteConfigData(remoteConfigParams)
                analyticsLogEvent(getAnalytics(app), event, {
                  ...params,
                  ...utmParameters,
                  ...remoteConfigParams,
                })
              }
          )
      })
    }
  }, [app, isFirebaseSupported])

  useEffect(() => {
    if (app && currentUserId && isFirebaseSupported) {
      setUserId(getAnalytics(app), currentUserId)
    }
  }, [app, currentUserId])
}

function useAnalytics() {
  return useContext(AnalyticsContext)
}

export default useAnalytics
