import {
  getAnalytics,
  initializeAnalytics,
  setUserId,
  logEvent as analyticsLogEvent,
  isSupported,
} from '@firebase/analytics'
import * as firebase from '@firebase/app'
import { useContext, useEffect, useState } from 'react'

import { firebaseConfig } from 'config/firebase'
import { AnalyticsContext } from 'context/analyticsContext'
import { Events } from 'core/FirebaseEvents/constants'

import useUtmQueryParams from './useUtmQueryParams'

export const useConfigureAnalytics = (currentUserId: string | undefined) => {
  // const [app, setApp] = useState<firebase.FirebaseApp | undefined>()
  const [isFirebaseSupported, setIsFirebaseSupported] = useState<boolean>(false)
  const { logEvent, setLogEvent, app, setApp } = useAnalytics()
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
      setApp && setApp(initializeApp)
      isFirebaseSupported &&
        initializeAnalytics(initializeApp, {
          config: {
            send_page_view: false,
          },
        })

      setLogEvent &&
        setLogEvent(
          () =>
            (
              event: string,
              params:
                | { [key: string]: string | boolean | string[] }
                | Record<string, never> = {}
            ) => {
              analyticsLogEvent(getAnalytics(initializeApp), event, {
                ...params,
                ...utmParameters,
              })
            }
        )
    }
  }, [app, isFirebaseSupported])

  useEffect(() => {
    if (app && currentUserId && isFirebaseSupported) {
      setUserId(getAnalytics(app), currentUserId)
    }
  }, [app, currentUserId])

  useEffect(() => {
    if (logEvent && Object.keys(utmParameters).length)
      logEvent(Events.UTM_TRACKING_CAMPAIGN)
  }, [logEvent, utmParameters])
}

function useAnalytics() {
  return useContext(AnalyticsContext)
}

export default useAnalytics
